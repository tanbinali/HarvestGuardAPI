from datetime import date
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
import csv
from .models import User, CropBatch, WeatherData, HealthScan, Achievement
from .serializers import (UserSerializer, CropBatchSerializer, WeatherDataSerializer, HealthScanSerializer,AchievementSerializer)
from rest_framework.parsers import MultiPartParser, FormParser


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Optional user viewset for extra user queries"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

class CropBatchViewSet(viewsets.ModelViewSet):
    """Crop batch management"""
    serializer_class = CropBatchSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CropBatch.objects.none()

        return CropBatch.objects.filter(farmer=self.request.user)

    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)
    
    @action(detail=False, methods=['GET'])
    def export_data(self, request):
        """Export user data as CSV or JSON"""
        format_type = request.query_params.get('format', 'json')
        batches = self.get_queryset()
        
        if format_type == 'csv':
            return self._export_csv(batches)
        else:
            return self._export_json(batches)
    
    def _export_csv(self, batches):
        response = Response(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="harvestguard_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Crop Type', 'Weight (kg)', 'Harvest Date', 
                        'Storage Location', 'Storage Type', 'Status', 'Created At'])
        
        for batch in batches:
            writer.writerow([batch.crop_type, batch.estimated_weight, 
                           batch.harvest_date, batch.storage_location,
                           batch.storage_type, batch.status, batch.created_at])
        
        return response
    
    def _export_json(self, batches):
        data = {
            'export_date': str(date.today()),
            'farmer_email': self.request.user.email,
            'batches': CropBatchSerializer(batches, many=True).data
        }
        return Response(data)
    
    @action(detail=False, methods=['GET'])
    def active(self, request):
        """Get only active batches"""
        batches = self.get_queryset().filter(status='ACTIVE')
        serializer = self.get_serializer(batches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def completed(self, request):
        """Get completed batches"""
        batches = self.get_queryset().filter(status='COMPLETED')
        serializer = self.get_serializer(batches, many=True)
        return Response(serializer.data)


class WeatherDataViewSet(viewsets.ReadOnlyModelViewSet):
    """Weather data viewing"""
    serializer_class = WeatherDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WeatherData.objects.none()

        batch_id = self.request.query_params.get('batch_id')
        if batch_id:
            return WeatherData.objects.filter(
                batch__farmer=self.request.user,
                batch__id=batch_id
            )
        return WeatherData.objects.filter(batch__farmer=self.request.user)

    @action(detail=False, methods=['POST'])
    def upload(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Achievement/badge management"""
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Achievement.objects.none()

        return Achievement.objects.filter(user=self.request.user)


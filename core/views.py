from datetime import date
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
import csv
from .models import User, CropBatch, Achievement, LossEvent, Intervention
from .serializers import (UserSerializer, CropBatchSerializer,AchievementSerializer, LossEventSerializer, InterventionSerializer)
from .achievements import award_badge


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
        batch = serializer.save(farmer=self.request.user)
        
        # Award "First Harvest Logged" badge
        if batch.farmer.crop_batches.count() == 1:
            award_badge(batch.farmer, 'FIRST_HARVEST')
    
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
    @action(detail=False, methods=['GET'])
    
    def dashboard(self, request):
        """Aggregate stats for profile page"""
        batches = self.get_queryset()
        total_batches = batches.count()
        total_loss_events = sum(b.loss_events.count() for b in batches)
        total_interventions = sum(b.interventions.count() for b in batches)
        successful_interventions = sum(b.interventions.filter(success=True).count() for b in batches)
        success_rate = (successful_interventions / total_interventions * 100) if total_interventions else 0

        data = {
            "total_batches": total_batches,
            "total_loss_events": total_loss_events,
            "total_interventions": total_interventions,
            "successful_interventions": successful_interventions,
            "intervention_success_rate": round(success_rate, 2)
        }
        return Response(data)

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Achievement/badge management"""
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Achievement.objects.none()

        return Achievement.objects.filter(user=self.request.user)

class LossEventViewSet(viewsets.ModelViewSet):
    """CRUD for loss events per crop batch"""
    serializer_class = LossEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LossEvent.objects.filter(batch__farmer=self.request.user)

    def perform_create(self, serializer):
        # Ensure the batch belongs to the current user
        serializer.save()

class InterventionViewSet(viewsets.ModelViewSet):
    """CRUD for interventions per crop batch"""
    serializer_class = InterventionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Intervention.objects.filter(batch__farmer=self.request.user)

    def perform_create(self, serializer):
        intervention = serializer.save()
        
        # Award "Risk Mitigated Expert" badge if intervention was successful
        if intervention.success:
            award_badge(intervention.batch.farmer, 'RISK_MITIGATOR')

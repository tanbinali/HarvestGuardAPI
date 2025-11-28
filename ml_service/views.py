from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from core.models import HealthScan, CropBatch
from core.serializers import HealthScanSerializer
from ml_service.services import CropHealthService

class HealthScanViewSet(viewsets.ModelViewSet):
    """
    Unified HealthScan ViewSet:
    - CRUD for HealthScan
    - Upload image + detect crop health
    """
    serializer_class = HealthScanSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        # Only scans for the current user's batches
        return HealthScan.objects.filter(batch__farmer=self.request.user)

    def get_serializer(self, *args, **kwargs):
        """
        Filter the batch dropdown to only show current user's batches
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(*args, **kwargs)

        # Use .child.fields if serializer is a ListSerializer
        fields = getattr(serializer, 'child', serializer).fields
        if 'batch' in fields and hasattr(fields['batch'], 'queryset'):
            fields['batch'].queryset = CropBatch.objects.filter(farmer=self.request.user)

        return serializer

    @action(detail=False, methods=['POST'])
    def upload_and_detect(self, request):
        """
        Upload an image, detect crop health, and create HealthScan
        """
        batch_id = request.data.get('batch_id')
        image = request.FILES.get('image')

        if not batch_id or not image:
            return Response(
                {'error': 'batch_id and image are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            batch = CropBatch.objects.get(id=batch_id, farmer=request.user)
        except CropBatch.DoesNotExist:
            return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)

        # Call ML service for detection
        ml_service = CropHealthService()
        detection_result = ml_service.detect_crop_health(image)

        # Save HealthScan record
        health_scan = HealthScan.objects.create(
            batch=batch,
            image=image,
            detection_result=detection_result['detection_result'],
            confidence=detection_result['confidence']
        )

        serializer = HealthScanSerializer(health_scan, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import CropBatch, WeatherData
from core.serializers import WeatherDataSerializer
from .services import WeatherService, RiskPredictionService


class WeatherViewSet(viewsets.ViewSet):
    """Weather forecast and risk prediction"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def forecast(self, request):
        # Prevent Swagger schema crash
        if getattr(request, 'swagger_fake_view', False):
            return Response({})
        
        batch_id = request.query_params.get('batch_id')
        
        try:
            batch = CropBatch.objects.get(id=batch_id, farmer=request.user)
        except CropBatch.DoesNotExist:
            return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch weather forecast
        weather_service = WeatherService()
        forecast = weather_service.get_forecast(batch.storage_location)
        
        # Save forecast into DB
        for day_forecast in forecast:
            WeatherData.objects.update_or_create(
                batch=batch,
                forecast_date=day_forecast['date'],
                defaults={
                    'temperature': day_forecast['temperature'],
                    'humidity': day_forecast['humidity'],
                    'rainfall_probability': day_forecast['rainfall_probability'],
                    'wind_speed': day_forecast['wind_speed'],
                    'description': day_forecast['description'],
                }
            )
        
        return Response({
            'batch_id': batch_id,
            'location': batch.storage_location,
            'forecast': forecast
        })
    
    @action(detail=False, methods=['GET'])
    def advisory(self, request):
        # Prevent Swagger crash
        if getattr(request, 'swagger_fake_view', False):
            return Response({})
        
        batch_id = request.query_params.get('batch_id')
        
        try:
            batch = CropBatch.objects.get(id=batch_id, farmer=request.user)
        except CropBatch.DoesNotExist:
            return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        weather_service = WeatherService()
        forecast = weather_service.get_forecast(batch.storage_location)
        advisories = weather_service.get_bangla_advisory(batch, forecast)
        
        return Response({
            'batch_id': batch_id,
            'advisories': advisories
        })
    
    @action(detail=False, methods=['GET'])
    def risk_assessment(self, request):
        # Prevent Swagger crash
        if getattr(request, 'swagger_fake_view', False):
            return Response({})
        
        batch_id = request.query_params.get('batch_id')
        
        try:
            batch = CropBatch.objects.get(id=batch_id, farmer=request.user)
        except CropBatch.DoesNotExist:
            return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Fetch forecast data
        weather_service = WeatherService()
        forecast = weather_service.get_forecast(batch.storage_location)
        
        # Compute ETCL & risk prediction
        risk_service = RiskPredictionService()
        risk_data = risk_service.calculate_etcl(batch, forecast)
        
        # Save risk prediction to batch
        batch.risk_prediction.update(**risk_data)
        
        return Response(risk_data)

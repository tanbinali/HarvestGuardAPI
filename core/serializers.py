from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, CropBatch, WeatherData, HealthScan, Achievement, RiskPrediction

class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration and profile"""
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'first_name', 'last_name', 
                  'preferred_language', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = ['id', 'temperature', 'humidity', 'rainfall_probability', 
                  'wind_speed', 'description', 'forecast_date']

class HealthScanSerializer(serializers.ModelSerializer):
    batch = serializers.PrimaryKeyRelatedField(
        queryset=CropBatch.objects.all(),
        write_only=True,
        required=True
    )
    image = serializers.ImageField()

    class Meta:
        model = HealthScan
        fields = ['id', 'batch', 'image', 'detection_result', 'confidence', 'timestamp']
        read_only_fields = ['detection_result', 'confidence', 'timestamp']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return obj.image_url



class RiskPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskPrediction
        fields = ['id', 'etcl_hours', 'risk_level', 'risk_factors', 'recommendations']


class CropBatchSerializer(serializers.ModelSerializer):
    weather_data = WeatherDataSerializer(many=True, read_only=True)
    health_scans = HealthScanSerializer(many=True, read_only=True)
    risk_prediction = RiskPredictionSerializer(read_only=True)
    
    class Meta:
        model = CropBatch
        fields = ['id', 'crop_type', 'estimated_weight', 'harvest_date', 
                  'storage_location', 'storage_type', 'status', 'notes',
                  'weather_data', 'health_scans', 'risk_prediction', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'badge_name', 'earned_at']

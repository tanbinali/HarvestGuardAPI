from rest_framework import serializers
from .models import CropBatch, Achievement, LossEvent, Intervention
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration and profile"""
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'first_name', 'last_name', 
                  'preferred_language', 'password', 'created_at','username']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if 'username' not in validated_data or not validated_data['username']:
            email = validated_data.get('email')
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            validated_data['username'] = username
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


class CropBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropBatch
        fields = ['id', 'crop_type', 'estimated_weight', 'harvest_date', 
                  'storage_location', 'storage_type', 'status', 'notes',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'badge_name', 'earned_at']

class LossEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = LossEvent
        fields = ['id', 'batch', 'event_date', 'loss_type', 'estimated_loss_kg', 'description']
        read_only_fields = ['id']

class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = ['id', 'batch', 'intervention_type', 'applied_date', 'success', 'notes']
        read_only_fields = ['id']

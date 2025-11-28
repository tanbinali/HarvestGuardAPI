from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    """Custom User model for farmers"""
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('BN', 'Bangla'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='BN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.phone_number})"


class CropBatch(models.Model):
    """Crop batch/harvest model"""
    CROP_TYPE_CHOICES = [
        ('PADDY', 'Paddy/Rice'),
    ]
    
    STORAGE_TYPE_CHOICES = [
        ('JUTE_BAG', 'Jute Bag Stack'),
        ('SILO', 'Silo'),
        ('OPEN_AREA', 'Open Area'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
    ]
    
    LOCATION_CHOICES = [
        ('DHAKA', 'Dhaka'),
        ('CHITTAGONG', 'Chittagong'),
        ('SYLHET', 'Sylhet'),
        ('RAJSHAHI', 'Rajshahi'),
        ('KHULNA', 'Khulna'),
        ('BARISHAL', 'Barishal'),
        ('RANGPUR', 'Rangpur'),
        ('MYMENSINGH', 'Mymensingh'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_batches')
    crop_type = models.CharField(max_length=20, choices=CROP_TYPE_CHOICES, default='PADDY')
    estimated_weight = models.FloatField(help_text="Weight in kg")
    harvest_date = models.DateField()
    storage_location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.farmer.email} - {self.crop_type} ({self.harvest_date})"


class WeatherData(models.Model):
    """Weather information for a batch"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(CropBatch, on_delete=models.CASCADE, related_name='weather_data')
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    rainfall_probability = models.FloatField(help_text="Rainfall probability percentage")
    wind_speed = models.FloatField(default=0, help_text="Wind speed in km/h")
    description = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    forecast_date = models.DateField()
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.batch.id} - {self.temperature}°C on {self.forecast_date}"


class HealthScan(models.Model):
    """Crop health scan results"""
    DETECTION_CHOICES = [
        ('FRESH', 'Fresh'),
        ('ROTTEN', 'Rotten'),
        ('PENDING', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(CropBatch, on_delete=models.CASCADE, related_name='health_scans')
    image = CloudinaryField('image', folder="health_scans")
    detection_result = models.CharField(max_length=20, choices=DETECTION_CHOICES, default='PENDING')
    confidence = models.FloatField(default=0, help_text="Confidence score 0-1")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.batch.id} - {self.detection_result}"


class Achievement(models.Model):
    """User achievements/badges"""
    BADGE_CHOICES = [
        ('FIRST_HARVEST', 'First Harvest Logged'),
        ('RISK_MITIGATOR', 'Risk Mitigated Expert'),
        ('SCANNER_MASTER', 'Health Scanner Master'),
        ('WEATHER_ANALYST', 'Weather Analyst'),
        ('DATA_KEEPER', 'Data Keeper'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    badge_name = models.CharField(max_length=50, choices=BADGE_CHOICES)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge_name')
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.badge_name}"


class RiskPrediction(models.Model):
    """Risk prediction data"""
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.OneToOneField(CropBatch, on_delete=models.CASCADE, related_name='risk_prediction')
    etcl_hours = models.IntegerField(help_text="Estimated Time to Critical Loss in hours")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    risk_factors = models.JSONField(default=dict, help_text="List of risk factors detected")
    recommendations = models.JSONField(default=list, help_text="List of recommendations")
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.batch.id} - Risk: {self.risk_level} (ETCL: {self.etcl_hours}h)"

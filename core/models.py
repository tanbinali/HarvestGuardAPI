from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """Custom User model for farmers"""
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('BN', 'Bangla'),
    ]
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
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

class LossEvent(models.Model):
    """Records any loss/damage to a crop batch"""
    LOSS_TYPE_CHOICES = [
        ('PEST', 'Pest Infestation'),
        ('DISEASE', 'Disease'),
        ('WEATHER', 'Weather Damage'),
        ('STORAGE', 'Storage Loss'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(CropBatch, on_delete=models.CASCADE, related_name='loss_events')
    event_date = models.DateField()
    loss_type = models.CharField(max_length=20, choices=LOSS_TYPE_CHOICES)
    estimated_loss_kg = models.FloatField()
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.batch} - {self.loss_type} ({self.estimated_loss_kg}kg)"


class Intervention(models.Model):
    """Tracks interventions applied to mitigate losses"""
    INTERVENTION_TYPE_CHOICES = [
        ('PESTICIDE', 'Pesticide Applied'),
        ('FUNGICIDE', 'Fungicide Applied'),
        ('IRRIGATION', 'Irrigation Adjustment'),
        ('STORAGE', 'Improved Storage'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(CropBatch, on_delete=models.CASCADE, related_name='interventions')
    intervention_type = models.CharField(max_length=30, choices=INTERVENTION_TYPE_CHOICES)
    applied_date = models.DateField()
    success = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-applied_date']
    
    def __str__(self):
        return f"{self.batch} - {self.intervention_type} ({'Success' if self.success else 'Failed'})"

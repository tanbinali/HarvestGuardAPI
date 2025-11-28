from django.contrib import admin
from .models import HealthScan, CropBatch, User, WeatherData, Achievement

# Register models so they appear in Django Admin
admin.site.register(User)
admin.site.register(CropBatch)
admin.site.register(HealthScan)
admin.site.register(WeatherData)
admin.site.register(Achievement)


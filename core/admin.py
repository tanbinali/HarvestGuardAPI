from django.contrib import admin
from .models import CropBatch, User, Achievement

# Register models so they appear in Django Admin
admin.site.register(User)
admin.site.register(CropBatch)
admin.site.register(Achievement)


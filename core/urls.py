from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, CropBatchViewSet, WeatherDataViewSet, AchievementViewSet)
from ml_service.views import HealthScanViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'crops/batches', CropBatchViewSet, basename='crop-batch')
router.register(r'weather', WeatherDataViewSet, basename='weather')
router.register(r'health-scans', HealthScanViewSet, basename='health-scan')
router.register(r'achievements', AchievementViewSet, basename='achievement')

# Schema view configuration for Swagger and Redoc API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Harvest Guard API",
      default_version='v1',
      description="API documentation for Harvest Guard application.",
      terms_of_service="https://www.harvestguard.com/terms/",
      contact=openapi.Contact(email="tanbinali@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (InterventionViewSet, LossEventViewSet, UserViewSet, CropBatchViewSet, AchievementViewSet)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'crops/batches', CropBatchViewSet, basename='crop-batch')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'loss-events', LossEventViewSet, basename='loss-event')
router.register(r'interventions', InterventionViewSet, basename='intervention')


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

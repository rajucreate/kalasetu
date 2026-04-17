"""
API URL routing.
Defines all REST API endpoints for frontend consumption.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    CurrentUserView,
    ProductViewSet,
    ArtisanViewSet,
    ArtisanStoryViewSet,
    ConsultantPendingView,
    ConsultantVerifyView,
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'artisans', ArtisanViewSet, basename='artisan')
router.register(r'stories', ArtisanStoryViewSet, basename='story')

urlpatterns = [
    # Authentication
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # User profile
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    
    # Consultant endpoints
    path('consultant/pending/', ConsultantPendingView.as_view(), name='consultant_pending'),
    path('consultant/verify/<int:product_id>/', ConsultantVerifyView.as_view(), name='consultant_verify'),
    
    # ViewSet routes
    path('', include(router.urls)),
]

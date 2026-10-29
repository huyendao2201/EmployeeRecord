from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import (
    LoginAPIView,
    QuickSwitchAPIView,
    CurrentUserAPIView,
    UserManagementViewSet
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user_management')

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='auth_login'),
    path('quick-switch/', QuickSwitchAPIView.as_view(), name='auth_quick_switch'),
    path('me/', CurrentUserAPIView.as_view(), name='auth_me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentProfileViewSet,
    AcademicRecordViewSet,
    AuditLogViewSet,
    SecurityStatsAPIView
)

router = DefaultRouter()
router.register(r'students', StudentProfileViewSet, basename='student')
router.register(r'grades', AcademicRecordViewSet, basename='grade')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('security/stats/', SecurityStatsAPIView.as_view(), name='security-stats'),
    path('', include(router.urls)),
]

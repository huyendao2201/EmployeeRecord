from django.urls import path, include
from rest_framework.routers import DefaultRouter
from employees.views import (
    EmployeeProfileViewSet,
    LaborContractViewSet,
    AuditLogViewSet,
    SecurityDashboardStatsView
)

router = DefaultRouter()
router.register(r'employees', EmployeeProfileViewSet, basename='employee')
router.register(r'contracts', LaborContractViewSet, basename='contract')
router.register(r'audit-logs', AuditLogViewSet, basename='audit_log')

urlpatterns = [
    path('security/stats/', SecurityDashboardStatsView.as_view(), name='security_stats'),
    path('', include(router.urls)),
]

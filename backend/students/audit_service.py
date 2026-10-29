from .models import AuditLog, AuditLogAction, AuditLogStatus
from .permissions import get_client_ip


def log_security_event(action, status, user=None, username_attempt="", request=None, resource_type="Auth", resource_id="", details=""):
    ip_addr = "127.0.0.1"
    if request:
        ip_addr = get_client_ip(request)

    return AuditLog.objects.create(
        user=user,
        username_attempt=username_attempt or (user.username if user else "Anonymous"),
        ip_address=ip_addr,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        details=details
    )

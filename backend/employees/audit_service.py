from employees.models import AuditLog, AuditLogAction, AuditLogStatus


def get_client_ip(request):
    """Lấy địa chỉ IP thực của client từ HTTP headers."""
    if not request:
        return '127.0.0.1'
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def log_security_event(
    action,
    status,
    user=None,
    username_attempt='',
    request=None,
    resource_type='',
    resource_id='',
    details=''
):
    """
    Hàm chuẩn hóa ghi nhận Audit Log cho toàn bộ hệ thống.
    Đảm bảo tính toàn vẹn (Immutability): chỉ thêm mới, không chỉnh sửa hay xóa log.
    """
    ip_address = get_client_ip(request)
    
    if user and not username_attempt:
        username_attempt = getattr(user, 'username', '')

    return AuditLog.objects.create(
        user=user if user and getattr(user, 'is_authenticated', False) else None,
        username_attempt=username_attempt,
        ip_address=ip_address,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        status=status,
        details=details
    )

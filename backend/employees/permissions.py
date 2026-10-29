from rest_framework import permissions
from accounts.models import UserRole
from employees.models import AuditLogAction, AuditLogStatus
from employees.audit_service import log_security_event


class IsOwnerOrHR(permissions.BasePermission):
    """
    Quyết định thiết kế 1 (QĐ1) - Chống IDOR:
    - Admin và HR có quyền truy cập toàn bộ hồ sơ.
    - Nhân viên (Employee) chỉ được phép truy cập hồ sơ của chính mình.
    - Nếu Nhân viên cố tình truy cập hồ sơ người khác bằng cách thay đổi ID trên API/URL (IDOR),
      hệ thống chặn ngay (403 Forbidden) và tự động ghi Audit Log cảnh báo an ninh.
    """
    message = "Bạn không có quyền truy cập hồ sơ này. Hành vi truy cập trái phép (IDOR) đã bị từ chối và ghi lại vào Nhật ký Kiểm toán."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin và HR có toàn quyền
        if user.role in [UserRole.ADMIN, UserRole.HR]:
            return True

        # Kế toán được xem (Safe methods: GET, HEAD, OPTIONS)
        if user.role == UserRole.ACCOUNTANT and request.method in permissions.SAFE_METHODS:
            return True

        # Xác định đối tượng profile thuộc về ai
        target_user = getattr(obj, 'user', None)
        if hasattr(obj, 'employee'):
            target_user = obj.employee.user

        is_owner = (target_user == user)

        if not is_owner:
            # Phát hiện tấn công IDOR!
            log_security_event(
                action=AuditLogAction.IDOR_ATTEMPT,
                status=AuditLogStatus.FORBIDDEN,
                user=user,
                request=request,
                resource_type=obj.__class__.__name__,
                resource_id=getattr(obj, 'id', ''),
                details=f"Người dùng '{user.username}' (Role: {user.role}) cố tình truy cập trái phép tài nguyên ID '{getattr(obj, 'id', '')}' thuộc sở hữu của '{getattr(target_user, 'username', 'khác')}'."
            )
            return False

        # Nhân viên là chủ sở hữu:
        # Được phép GET (xem) hoặc PUT/PATCH các trường thông tin cá nhân cơ bản
        return True


class IsAdminOrHR(permissions.BasePermission):
    """Chỉ Quản trị viên hoặc Nhân sự mới có quyền truy cập."""
    message = "Bạn không có quyền thực hiện thao tác này. Chức năng chỉ dành cho Quản trị viên hoặc Quản lý Nhân sự."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.ADMIN, UserRole.HR]
        )


class ReadOnlyAuditLogPermission(permissions.BasePermission):
    """
    Đảm bảo tính toàn vẹn (Immutability) của Audit Log:
    - Chỉ cho phép Admin/HR xem nhật ký (GET, HEAD, OPTIONS).
    - Cấm tuyệt đối các thao tác tạo mới (POST), sửa đổi (PUT/PATCH), hoặc xóa (DELETE) qua API.
    """
    message = "Bạn không có quyền chỉnh sửa hoặc thay đổi dữ liệu trong Nhật ký Kiểm toán."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return False
        return request.method in permissions.SAFE_METHODS

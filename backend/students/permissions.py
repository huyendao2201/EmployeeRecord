from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import AuditLog, AuditLogAction, AuditLogStatus


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


class IsOwnerOrRegistrar(permissions.BasePermission):
    """
    QĐ1 (Trọng tâm): Phân quyền cấp đối tượng (Object-Level Permission).
    - Admin, Giáo vụ (Registrar), Giảng viên: Có quyền quản lý hồ sơ sinh viên theo chức năng.
    - Sinh viên (STUDENT): Chỉ được phép xem/sửa hồ sơ của CHÍNH MÌNH.
    - Nếu cố tình can thiệp ID hồ sơ sinh viên khác -> Chặn đứng HTTP 403 và ghi vết IDOR vào Audit Log.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Thao tác trên Bảng điểm (AcademicRecord)
        if getattr(view, 'basename', '') == 'grade':
            if request.method == 'POST':
                # Admin, Giáo vụ và Giảng viên được phép nhập điểm
                return request.user.role in ['ADMIN', 'REGISTRAR', 'TEACHER']
            if request.method == 'DELETE':
                return request.user.role in ['ADMIN', 'REGISTRAR']
            return True

        # Thao tác trên Hồ sơ Sinh viên (StudentProfile)
        # Chỉ Giáo vụ hoặc Admin mới có quyền tạo mới sinh viên (POST) hoặc xóa (DELETE)
        if request.method in ['POST', 'DELETE']:
            return request.user.role in ['ADMIN', 'REGISTRAR']
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin và Giáo vụ có toàn quyền trên mọi hồ sơ sinh viên và điểm số
        if user.role in ['ADMIN', 'REGISTRAR']:
            return True

        # Giảng viên
        if user.role == 'TEACHER':
            # Giảng viên có quyền sửa/nhập điểm môn học
            if hasattr(obj, 'student'):
                return True
            # Đối với hồ sơ sinh viên: Giảng viên chỉ được xem (SAFE_METHODS)
            return request.method in permissions.SAFE_METHODS

        # Xác định chủ sở hữu của tài nguyên (StudentProfile hoặc AcademicRecord)
        target_user = getattr(obj, 'user', None)
        target_name = getattr(obj, 'full_name', '')
        target_code = getattr(obj, 'student_code', '')
        resource_type = obj.__class__.__name__

        if hasattr(obj, 'student'):
            target_user = obj.student.user
            target_name = obj.student.full_name
            target_code = obj.student.student_code

        is_owner = (target_user == user)

        if not is_owner:
            # GHI NHẬT KÝ KIỂM TOÁN TỨC THÌ (Audit Log - QĐ4)
            AuditLog.objects.create(
                user=user,
                username_attempt=user.username,
                ip_address=get_client_ip(request),
                action=AuditLogAction.IDOR_ATTEMPT,
                resource_type=resource_type,
                resource_id=str(obj.id),
                status=AuditLogStatus.FORBIDDEN,
                details=f"Cảnh báo IDOR: Sinh viên '{user.username}' (Vai trò: {user.role}) cố tình truy xuất trái phép tài nguyên '{resource_type}' của sinh viên '{target_name}' (MSSV: {target_code} - ID: {obj.id}). Gói tin đã bị chặn đứng ở cấp máy chủ."
            )
            raise PermissionDenied(f"QĐ1 - Truy cập bị từ chối: Bạn không có quyền truy xuất hoặc chỉnh sửa tài nguyên của sinh viên khác!")

        return True


class ReadOnlyAuditLogPermission(permissions.BasePermission):
    """
    QĐ4: Tính toàn vẹn của Nhật ký kiểm toán (WORM - Write Once, Read Many).
    Chỉ cho phép đọc (SAFE_METHODS). Cấm mọi thao tác ghi, sửa, xóa qua API.
    """

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            return False
        if not request.user or not request.user.is_authenticated:
            return False
        # Chỉ Giáo vụ hoặc Admin mới được xem Audit Log
        return request.user.role in ['ADMIN', 'REGISTRAR']

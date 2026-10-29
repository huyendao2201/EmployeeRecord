from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, UserRole
from accounts.serializers import (
    UserSerializer,
    UserManagementSerializer,
    LoginRequestSerializer,
    QuickSwitchRequestSerializer
)
from employees.audit_service import log_security_event
from employees.models import AuditLogAction, AuditLogStatus


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    # Thêm custom claims vào token
    refresh['username'] = user.username
    refresh['role'] = user.role
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginAPIView(APIView):
    """
    QĐ3: Bảo vệ xác thực & Phòng thủ tấn công Brute-force:
    - Kiểm tra trạng thái khóa của tài khoản.
    - Giới hạn tối đa 5 lần thử sai liên tiếp.
    - Khóa tạm thời 5 phút nếu vượt quá ngưỡng và ghi nhận sự kiện vào Audit Log.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username'].strip()
        password = serializer.validated_data['password']

        user = User.objects.filter(username=username).first()

        # 1. Kiểm tra tài khoản có bị khóa không
        if user and user.is_locked():
            remaining_seconds = int((user.locked_until - timezone.now()).total_seconds())
            remaining_mins = max(1, remaining_seconds // 60)
            
            # Ghi log cảnh báo cố đăng nhập khi bị khóa
            log_security_event(
                action=AuditLogAction.LOGIN_FAILED,
                status=AuditLogStatus.WARNING,
                user=user,
                username_attempt=username,
                request=request,
                resource_type='Auth',
                details=f"Tài khoản '{username}' đang bị khóa do thử sai quá nhiều lần. Cố đăng nhập lại (còn {remaining_mins} phút)."
            )

            return Response({
                "error": "Tài khoản tạm thời bị khóa do nhập sai mật khẩu quá 5 lần!",
                "is_locked": True,
                "remaining_minutes": remaining_mins,
                "detail": f"Vui lòng thử lại sau {remaining_mins} phút hoặc liên hệ Quản trị viên."
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 2. Thực hiện xác thực
        authenticated_user = authenticate(username=username, password=password)

        if not authenticated_user:
            if user:
                user.increment_failed_attempts(max_attempts=5, lock_minutes=5)
                attempts_left = max(0, 5 - user.failed_login_attempts)

                if user.is_locked():
                    log_security_event(
                        action=AuditLogAction.ACCOUNT_LOCKED,
                        status=AuditLogStatus.WARNING,
                        user=user,
                        username_attempt=username,
                        request=request,
                        resource_type='Auth',
                        details=f"Tài khoản '{username}' chính thức bị khóa 5 phút sau 5 lần nhập sai mật khẩu liên tiếp."
                    )
                    return Response({
                        "error": "Mật khẩu không chính xác! Tài khoản đã bị tạm khóa 5 phút do vi phạm ngưỡng an toàn (5 lần).",
                        "is_locked": True,
                        "failed_attempts": user.failed_login_attempts
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    log_security_event(
                        action=AuditLogAction.LOGIN_FAILED,
                        status=AuditLogStatus.FAILED,
                        user=user,
                        username_attempt=username,
                        request=request,
                        resource_type='Auth',
                        details=f"Đăng nhập thất bại cho user '{username}'. Đã sai {user.failed_login_attempts}/5 lần."
                    )
                    return Response({
                        "error": f"Mật khẩu không chính xác! Bạn còn {attempts_left} lần thử trước khi tài khoản bị khóa.",
                        "is_locked": False,
                        "attempts_left": attempts_left
                    }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # User không tồn tại trên hệ thống
                log_security_event(
                    action=AuditLogAction.LOGIN_FAILED,
                    status=AuditLogStatus.FAILED,
                    username_attempt=username,
                    request=request,
                    resource_type='Auth',
                    details=f"Cố gắng đăng nhập với tài khoản không tồn tại '{username}'."
                )
                return Response({
                    "error": "Tài khoản hoặc mật khẩu không chính xác!",
                    "is_locked": False
                }, status=status.HTTP_401_UNAUTHORIZED)

        # 3. Đăng nhập thành công
        authenticated_user.reset_failed_attempts()
        tokens = get_tokens_for_user(authenticated_user)
        user_data = UserSerializer(authenticated_user).data

        log_security_event(
            action=AuditLogAction.LOGIN_SUCCESS,
            status=AuditLogStatus.SUCCESS,
            user=authenticated_user,
            request=request,
            resource_type='Auth',
            details=f"Đăng nhập thành công với vai trò '{authenticated_user.get_role_display()}'."
        )

        return Response({
            "message": "Đăng nhập thành công!",
            "tokens": tokens,
            "user": user_data
        }, status=status.HTTP_200_OK)


class QuickSwitchAPIView(APIView):
    """
    Công cụ hỗ trợ thuyết trình 5 phút:
    Cho phép chuyển đổi tức thì giữa các tài khoản demo (Nhân viên A, B, HR, Admin)
    để minh họa trực quan sự phân quyền và bảo mật trên slide & web.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = QuickSwitchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        user = User.objects.filter(username=username).first()
        if not user:
            return Response({"error": f"Không tìm thấy tài khoản demo '{username}'"}, status=status.HTTP_404_NOT_FOUND)

        # Mở khóa nếu tài khoản đang bị khóa để tiện demo
        if user.is_locked():
            user.reset_failed_attempts()

        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data

        log_security_event(
            action=AuditLogAction.LOGIN_SUCCESS,
            status=AuditLogStatus.SUCCESS,
            user=user,
            request=request,
            resource_type='Auth',
            details=f"[Demo Fast-Switch] Chuyển đổi nhanh sang tài khoản '{user.username}' ({user.get_role_display()})."
        )

        return Response({
            "message": f"Chuyển đổi thành công sang tài khoản {user.username}!",
            "tokens": tokens,
            "user": user_data
        }, status=status.HTTP_200_OK)


class CurrentUserAPIView(APIView):
    """Lấy thông tin tài khoản hiện tại kèm profile ID."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    Quản lý tài khoản đăng nhập của nhân viên:
    - Xem danh sách tài khoản, thông tin đăng nhập, vai trò, số lần nhập sai.
    - Cập nhật vai trò (Role), trạng thái kích hoạt (is_active), tên đăng nhập (username).
    - Đặt lại mật khẩu (Reset password).
    - Khóa / Mở khóa tài khoản (Toggle Lock / Reset brute-force lockout).
    Chỉ Quản trị viên (Admin) hoặc Quản lý Nhân sự (HR) mới có quyền truy cập.
    """
    queryset = User.objects.all().select_related('profile').order_by('id')
    serializer_class = UserManagementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_admin_or_hr(self, request):
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response(
                {"error": "Bạn không có quyền quản lý tài khoản người dùng. Chức năng chỉ dành cho Admin hoặc HR."},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def list(self, request, *args, **kwargs):
        perm_error = self.check_admin_or_hr(request)
        if perm_error:
            return perm_error
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        perm_error = self.check_admin_or_hr(request)
        if perm_error and request.user.id != int(kwargs.get('pk', 0)):
            return perm_error
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        perm_error = self.check_admin_or_hr(request)
        if perm_error:
            return perm_error

        target_user = self.get_object()
        new_role = request.data.get('role')
        new_is_active = request.data.get('is_active')
        new_username = request.data.get('username')

        # Phòng ngừa tự hạ quyền nếu là tài khoản Admin hiện tại
        if target_user == request.user and new_role and new_role != target_user.role:
            return Response(
                {"error": "Bạn không thể tự thay đổi vai trò của tài khoản đang đăng nhập."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_username and new_username != target_user.username:
            if User.objects.filter(username=new_username).exclude(id=target_user.id).exists():
                return Response(
                    {"error": f"Tên đăng nhập '{new_username}' đã được sử dụng bởi người dùng khác."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            old_un = target_user.username
            target_user.username = new_username
            log_security_event(
                action=AuditLogAction.SYSTEM_CONFIG,
                status=AuditLogStatus.SUCCESS,
                user=request.user,
                request=request,
                resource_type='UserAccount',
                resource_id=target_user.id,
                details=f"Admin/HR '{request.user.username}' đã đổi tên đăng nhập từ '{old_un}' thành '{new_username}'."
            )

        if new_role and new_role in UserRole.values:
            old_role = target_user.get_role_display()
            target_user.role = new_role
            new_role_display = target_user.get_role_display()
            log_security_event(
                action=AuditLogAction.SYSTEM_CONFIG,
                status=AuditLogStatus.SUCCESS,
                user=request.user,
                request=request,
                resource_type='UserAccount',
                resource_id=target_user.id,
                details=f"Thay đổi vai trò tài khoản '{target_user.username}' từ '{old_role}' thành '{new_role_display}'."
            )

        if new_is_active is not None:
            target_user.is_active = bool(new_is_active)
            status_text = "Kích hoạt" if target_user.is_active else "Vô hiệu hóa"
            log_security_event(
                action=AuditLogAction.SYSTEM_CONFIG,
                status=AuditLogStatus.SUCCESS,
                user=request.user,
                request=request,
                resource_type='UserAccount',
                resource_id=target_user.id,
                details=f"{status_text} tài khoản đăng nhập '{target_user.username}'."
            )

        target_user.save()
        serializer = self.get_serializer(target_user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        perm_error = self.check_admin_or_hr(request)
        if perm_error:
            return perm_error

        target_user = self.get_object()
        new_password = request.data.get('new_password', '').strip()

        if not new_password or len(new_password) < 6:
            return Response(
                {"error": "Mật khẩu mới phải có độ dài tối thiểu từ 6 ký tự."},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_user.set_password(new_password)
        target_user.reset_failed_attempts()
        target_user.is_active = True
        target_user.save()

        log_security_event(
            action=AuditLogAction.SYSTEM_CONFIG,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='UserAccount',
            resource_id=target_user.id,
            details=f"Admin/HR '{request.user.username}' đã đặt lại mật khẩu cho tài khoản '{target_user.username}'."
        )

        return Response({
            "message": f"Đặt lại mật khẩu cho tài khoản '{target_user.username}' thành công!",
            "username": target_user.username
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-lock')
    def toggle_lock(self, request, pk=None):
        perm_error = self.check_admin_or_hr(request)
        if perm_error:
            return perm_error

        target_user = self.get_object()
        if target_user == request.user:
            return Response(
                {"error": "Không thể tự khóa tài khoản của chính mình."},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_currently_locked = target_user.is_locked() or not target_user.is_active

        if is_currently_locked:
            target_user.reset_failed_attempts()
            target_user.is_active = True
            target_user.save()
            action_desc = "Mở khóa tài khoản"
        else:
            target_user.is_active = False
            target_user.locked_until = timezone.now() + timezone.timedelta(days=365)
            target_user.save()
            action_desc = "Khóa tài khoản"

        log_security_event(
            action=AuditLogAction.ACCOUNT_LOCKED if not is_currently_locked else AuditLogAction.SYSTEM_CONFIG,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='UserAccount',
            resource_id=target_user.id,
            details=f"Admin/HR '{request.user.username}' đã thực hiện '{action_desc}' đối với tài khoản '{target_user.username}'."
        )

        serializer = self.get_serializer(target_user)
        return Response({
            "message": f"Đã {action_desc.lower()} '{target_user.username}' thành công!",
            "user": serializer.data
        }, status=status.HTTP_200_OK)

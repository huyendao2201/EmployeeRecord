from django.utils import timezone
from django.http import FileResponse
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from accounts.models import User, UserRole
from employees.models import (
    EmployeeProfile, LaborContract, ContractType, ContractStatus,
    AuditLog, AuditLogAction, AuditLogStatus
)
from employees.serializers import (
    EmployeeProfileSerializer,
    LaborContractSerializer,
    AuditLogSerializer
)
from employees.permissions import IsOwnerOrHR, ReadOnlyAuditLogPermission
from employees.audit_service import log_security_event


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet Quản lý Hồ sơ nhân viên có tích hợp cơ chế phòng thủ IDOR (QĐ1)
    và Ghi nhật ký tự động (QĐ4).
    """
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsOwnerOrHR]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return EmployeeProfile.objects.none()

        # Đối với các thao tác truy xuất chi tiết, cho phép queryset tìm đối tượng
        # để lớp phân quyền Object-level Permission (IsOwnerOrHR) bắt và chặn IDOR với mã 403 Forbidden
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return EmployeeProfile.objects.select_related('user').all()

        # Admin, HR và Kế toán được xem danh sách đầy đủ
        if user.role in [UserRole.ADMIN, UserRole.HR, UserRole.ACCOUNTANT]:
            return EmployeeProfile.objects.select_related('user').all().order_by('employee_code')

        # Nhân viên thông thường chỉ thấy hồ sơ của mình trong danh sách
        return EmployeeProfile.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        # DRF tự động gọi get_object() -> check_object_permissions()
        # Nếu vi phạm IDOR, permission class sẽ chặn và ném 403 Forbidden kèm ghi log
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Ghi log xem hồ sơ hợp lệ
        log_security_event(
            action=AuditLogAction.VIEW_PROFILE,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='EmployeeProfile',
            resource_id=instance.id,
            details=f"Xem thông tin hồ sơ nhân viên '{instance.full_name}' ({instance.employee_code})."
        )
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Ghi log cập nhật hồ sơ
        log_security_event(
            action=AuditLogAction.UPDATE_PROFILE,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='EmployeeProfile',
            resource_id=instance.id,
            details=f"Cập nhật thành công thông tin hồ sơ '{instance.full_name}'."
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Thêm nhân viên mới (Chỉ dành cho Admin hoặc HR)."""
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response(
                {"error": "Bạn không có quyền thêm nhân sự. Thao tác chỉ dành cho Quản trị viên (Admin) hoặc Nhân sự (HR)."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        employee_code = (data.get('employee_code') or '').strip().upper()
        full_name = (data.get('full_name') or '').strip()
        phone = (data.get('phone') or '').strip()
        identity_card = (data.get('identity_card') or '').strip()
        department = (data.get('department') or 'Phòng Công nghệ & Phần mềm').strip()
        position = (data.get('position') or 'Chuyên viên').strip()
        email = (data.get('email') or '').strip()
        basic_salary = data.get('basic_salary', 15000000)
        salary_coefficient = data.get('salary_coefficient', 1.5)

        if not employee_code or not full_name:
            return Response({"error": "Vui lòng nhập đầy đủ Mã nhân viên và Họ và tên."}, status=status.HTTP_400_BAD_REQUEST)

        if EmployeeProfile.objects.filter(employee_code=employee_code).exists():
            return Response({"error": f"Mã nhân viên '{employee_code}' đã tồn tại trong hệ thống!"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Tạo hoặc lấy tài khoản User liên kết
        username = (data.get('username') or employee_code.lower()).strip()
        password = data.get('password') or 'Employee@123'
        user_role = data.get('role') or UserRole.EMPLOYEE

        user = User.objects.filter(username=username).first()
        if not user:
            name_parts = full_name.split()
            first_name = name_parts[-1] if name_parts else username
            last_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""
            user = User.objects.create_user(
                username=username,
                email=email or f"{username}@company.vn",
                password=password,
                role=user_role,
                first_name=first_name,
                last_name=last_name
            )

        # 2. Tạo EmployeeProfile
        profile = EmployeeProfile.objects.create(
            user=user,
            employee_code=employee_code,
            full_name=full_name,
            dob=data.get('dob') or None,
            phone=phone,
            email=email or user.email,
            identity_card=identity_card,
            address=data.get('address', ''),
            department=department,
            position=position,
            salary_coefficient=salary_coefficient,
            basic_salary=basic_salary,
            bank_account=data.get('bank_account', ''),
            bank_name=data.get('bank_name', '')
        )

        # 3. Tạo hợp đồng lao động ban đầu
        LaborContract.objects.create(
            employee=profile,
            contract_number=f"HDLD-{employee_code}",
            contract_type=data.get('contract_type', ContractType.ONE_YEAR),
            start_date=data.get('start_date') or timezone.now().date(),
            salary_rate=basic_salary,
            status=ContractStatus.ACTIVE
        )

        # 4. Ghi Audit Log
        log_security_event(
            action=AuditLogAction.CREATE_PROFILE,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='EmployeeProfile',
            resource_id=profile.id,
            details=f"Admin/HR '{request.user.username}' đã thêm thành công hồ sơ nhân viên mới '{full_name}' ({employee_code})."
        )

        return Response(EmployeeProfileSerializer(profile).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Xóa hồ sơ nhân viên (Chỉ Admin hoặc HR)."""
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response(
                {"error": "Bạn không có quyền xóa nhân sự."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        emp_name = instance.full_name
        emp_code = instance.employee_code
        emp_id = instance.id
        user_to_delete = instance.user

        self.perform_destroy(instance)
        if user_to_delete and user_to_delete.role == UserRole.EMPLOYEE:
            user_to_delete.delete()

        log_security_event(
            action=AuditLogAction.DELETE_PROFILE,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='EmployeeProfile',
            resource_id=emp_id,
            details=f"Admin '{request.user.username}' đã xóa nhân viên '{emp_name}' ({emp_code})."
        )
        return Response({"message": f"Đã xóa thành công nhân viên {emp_name}."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response({"error": "Chỉ Admin hoặc HR mới có quyền đặt lại mật khẩu nhân viên."}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object()
        user = profile.user
        if not user:
            return Response({"error": "Hồ sơ này chưa liên kết tài khoản người dùng."}, status=status.HTTP_400_BAD_REQUEST)
        new_password = request.data.get('new_password', '').strip()
        if not new_password or len(new_password) < 6:
            return Response({"error": "Mật khẩu mới phải có tối thiểu 6 ký tự."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.reset_failed_attempts()
        user.is_active = True
        user.save()
        log_security_event(
            action=AuditLogAction.SYSTEM_CONFIG,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='UserAccount',
            resource_id=user.id,
            details=f"Admin/HR '{request.user.username}' đã đặt lại mật khẩu cho nhân viên '{profile.full_name}' ({user.username})."
        )
        return Response({"message": f"Đặt lại mật khẩu cho nhân viên {profile.full_name} ({user.username}) thành công!"})

    @action(detail=True, methods=['post'], url_path='toggle-lock')
    def toggle_lock(self, request, pk=None):
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response({"error": "Chỉ Admin hoặc HR mới có quyền khóa/mở khóa tài khoản nhân viên."}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object()
        user = profile.user
        if not user:
            return Response({"error": "Hồ sơ này chưa liên kết tài khoản người dùng."}, status=status.HTTP_400_BAD_REQUEST)
        if user == request.user:
            return Response({"error": "Không thể tự khóa tài khoản của chính mình."}, status=status.HTTP_400_BAD_REQUEST)
        is_currently_locked = user.is_locked() or not user.is_active
        if is_currently_locked:
            user.reset_failed_attempts()
            user.is_active = True
            user.save()
            action_desc = "Mở khóa tài khoản"
        else:
            user.is_active = False
            user.locked_until = timezone.now() + timezone.timedelta(days=365)
            user.save()
            action_desc = "Khóa tài khoản"
        log_security_event(
            action=AuditLogAction.ACCOUNT_LOCKED if not is_currently_locked else AuditLogAction.SYSTEM_CONFIG,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='UserAccount',
            resource_id=user.id,
            details=f"Admin/HR '{request.user.username}' đã thực hiện '{action_desc}' nhân viên '{profile.full_name}' ({user.username})."
        )
        return Response({
            "message": f"Đã {action_desc.lower()} cho nhân viên {profile.full_name} thành công!",
            "is_active": user.is_active,
            "is_locked": user.is_locked()
        })

    @action(detail=True, methods=['patch'], url_path='update-account')
    def update_account(self, request, pk=None):
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response({"error": "Chỉ Admin hoặc HR mới có quyền sửa tài khoản nhân viên."}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object()
        user = profile.user
        if not user:
            return Response({"error": "Hồ sơ này chưa liên kết tài khoản."}, status=status.HTTP_400_BAD_REQUEST)
        role = request.data.get('role')
        username = request.data.get('username')
        if role and role in UserRole.values:
            if user == request.user and role != user.role:
                return Response({"error": "Không thể tự thay đổi vai trò tài khoản của chính mình."}, status=status.HTTP_400_BAD_REQUEST)
            user.role = role
        if username and username != user.username:
            from accounts.models import User
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                return Response({"error": f"Tên đăng nhập '{username}' đã được sử dụng."}, status=status.HTTP_400_BAD_REQUEST)
            user.username = username
        user.save()
        log_security_event(
            action=AuditLogAction.SYSTEM_CONFIG,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='UserAccount',
            resource_id=user.id,
            details=f"Cập nhật tài khoản đăng nhập của nhân viên '{profile.full_name}' (Username: {user.username}, Vai trò: {user.get_role_display()})."
        )
        return Response(EmployeeProfileSerializer(profile).data)



class LaborContractViewSet(viewsets.ModelViewSet):
    """ViewSet Quản lý Hợp đồng lao động với phân quyền chặt chẽ và lưu trữ tệp đính kèm."""
    serializer_class = LaborContractSerializer
    permission_classes = [IsOwnerOrHR]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return LaborContract.objects.none()

        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'download_file']:
            return LaborContract.objects.select_related('employee__user').all()

        if user.role in [UserRole.ADMIN, UserRole.HR, UserRole.ACCOUNTANT]:
            return LaborContract.objects.select_related('employee').all().order_by('-start_date')

        return LaborContract.objects.filter(employee__user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        log_security_event(
            action=AuditLogAction.VIEW_CONTRACT,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='LaborContract',
            resource_id=instance.id,
            details=f"Xem hợp đồng lao động số '{instance.contract_number}'."
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response(
                {"error": "Chỉ Quản trị viên (Admin) hoặc Nhân sự (HR) mới có quyền tạo hợp đồng lao động."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        file_note = f" (Kèm tệp: {instance.contract_file.name})" if instance.contract_file else ""
        log_security_event(
            action=AuditLogAction.UPDATE_CONTRACT,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='LaborContract',
            resource_id=instance.id,
            details=f"Tạo hợp đồng lao động mới số '{instance.contract_number}' cho nhân viên '{instance.employee.full_name}'{file_note}."
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if request.user.role not in [UserRole.ADMIN, UserRole.HR]:
            return Response(
                {"error": "Chỉ Quản trị viên (Admin) hoặc Nhân sự (HR) mới có quyền sửa hợp đồng lao động."},
                status=status.HTTP_403_FORBIDDEN
            )
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        file_note = f" (Cập nhật tệp: {instance.contract_file.name})" if instance.contract_file else ""
        log_security_event(
            action=AuditLogAction.UPDATE_CONTRACT,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='LaborContract',
            resource_id=instance.id,
            details=f"Cập nhật hợp đồng lao động số '{instance.contract_number}'{file_note}."
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='download')
    def download_file(self, request, pk=None):
        """
        Tải xuống hoặc xem tệp đính kèm hợp đồng có kiểm soát phân quyền (Object-level):
        Nhân viên chỉ tải được tệp hợp đồng của chính mình, HR/Admin tải được toàn bộ.
        """
        instance = self.get_object()
        if not instance.contract_file:
            return Response({"error": "Hợp đồng này chưa được đính kèm tệp văn bản/ảnh."}, status=status.HTTP_404_NOT_FOUND)

        import os
        import mimetypes
        file_path = instance.contract_file.path
        if not os.path.exists(file_path):
            return Response({"error": "Tệp hợp đồng không tồn tại trên hệ thống máy chủ."}, status=status.HTTP_404_NOT_FOUND)

        filename = os.path.basename(instance.contract_file.name)
        mode = request.query_params.get('mode', 'download')
        as_attachment = (mode != 'view')

        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'

        log_security_event(
            action=AuditLogAction.VIEW_CONTRACT,
            status=AuditLogStatus.SUCCESS,
            user=request.user,
            request=request,
            resource_type='LaborContractFile',
            resource_id=instance.id,
            details=f"{'Xem trực tiếp' if not as_attachment else 'Tải xuống'} tệp văn bản hợp đồng '{filename}' thuộc HĐ số '{instance.contract_number}'."
        )
        return FileResponse(instance.contract_file.open('rb'), as_attachment=as_attachment, filename=filename, content_type=content_type)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet Giám sát Audit Log:
    - Đảm bảo tính toàn vẹn (Immutability): Chỉ cho phép đọc (GET), cấm POST/PUT/DELETE.
    - Chỉ tài khoản Quản trị viên (Admin) hoặc HR mới có quyền xem.
    """
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [ReadOnlyAuditLogPermission]


class SecurityDashboardStatsView(APIView):
    """API tổng hợp số liệu an ninh và hoạt động cho Dashboard."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        total_employees = EmployeeProfile.objects.count()
        total_contracts = LaborContract.objects.count()
        
        total_logs = AuditLog.objects.count()
        idor_attempts = AuditLog.objects.filter(action=AuditLogAction.IDOR_ATTEMPT).count()
        locked_accounts = AuditLog.objects.filter(action=AuditLogAction.ACCOUNT_LOCKED).count()
        failed_logins = AuditLog.objects.filter(action=AuditLogAction.LOGIN_FAILED).count()

        return Response({
            "total_employees": total_employees,
            "total_contracts": total_contracts,
            "total_logs": total_logs,
            "idor_attempts": idor_attempts,
            "locked_accounts": locked_accounts,
            "failed_logins": failed_logins,
            "user_role": user.role,
            "current_user": user.username
        })

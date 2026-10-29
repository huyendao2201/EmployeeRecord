import re
from rest_framework import serializers
from accounts.models import UserRole
from employees.models import EmployeeProfile, LaborContract, AuditLog


class EmployeeProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    current_password = serializers.SerializerMethodField(read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    user_role_display = serializers.CharField(source='user.get_role_display', read_only=True)
    user_is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    user_is_locked = serializers.SerializerMethodField(read_only=True)
    user_failed_attempts = serializers.IntegerField(source='user.failed_login_attempts', read_only=True)
    user_last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    user_date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user', 'username', 'current_password', 'user_role', 'user_role_display',
            'user_is_active', 'user_is_locked', 'user_failed_attempts',
            'user_last_login', 'user_date_joined',
            'employee_code', 'full_name', 'dob', 'phone', 'email', 'identity_card',
            'address', 'department', 'position', 'salary_coefficient',
            'basic_salary', 'bank_account', 'bank_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'current_password', 'created_at', 'updated_at']

    def get_user_is_locked(self, obj):
        return obj.user.is_locked() if obj.user else False

    def get_current_password(self, obj):
        if obj.user and hasattr(obj.user, 'raw_password'):
            return obj.user.raw_password or 'Employee@123'
        return 'Employee@123'


    def validate_phone(self, value):
        """QĐ2: Xác thực định dạng số điện thoại an toàn."""
        cleaned = value.strip()
        if not re.match(r'^(0|\+84)[0-9]{9,10}$', cleaned):
            raise serializers.ValidationError("Số điện thoại không đúng định dạng Việt Nam (10 chữ số).")
        return cleaned

    def validate_identity_card(self, value):
        """QĐ2: Xác thực CCCD/CMND (chỉ gồm 9 hoặc 12 chữ số, chống SQLi / XSS)."""
        cleaned = value.strip()
        if not re.match(r'^[0-9]{9,12}$', cleaned):
            raise serializers.ValidationError("Số CCCD/CMND phải là dãy 9 hoặc 12 chữ số hợp lệ.")
        return cleaned

    def validate(self, attrs):
        """
        Kiểm tra quyền cập nhật trường nhạy cảm:
        Nhân viên không thể tự ý sửa hệ số lương hoặc lương cơ bản của mình!
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            if user.role == UserRole.EMPLOYEE:
                if 'basic_salary' in attrs or 'salary_coefficient' in attrs:
                    raise serializers.ValidationError({
                        "security_violation": "Bạn không có quyền thay đổi thông tin lương thưởng. Chỉ HR mới có quyền này."
                    })
        return attrs


class LaborContractSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contract_file_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LaborContract
        fields = [
            'id', 'employee', 'employee_name', 'employee_code',
            'contract_number', 'contract_type', 'contract_type_display',
            'start_date', 'end_date', 'salary_rate', 'status',
            'status_display', 'notes', 'contract_file', 'contract_file_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_contract_file_name(self, obj):
        if obj.contract_file:
            import os
            return os.path.basename(obj.contract_file.name)
        return None


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', default='', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'username_attempt', 'ip_address',
            'action', 'action_display', 'resource_type', 'resource_id',
            'status', 'status_display', 'details', 'timestamp'
        ]
        read_only_fields = fields

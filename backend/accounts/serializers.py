from rest_framework import serializers
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'role_display',
            'first_name', 'last_name', 'profile_id',
            'failed_login_attempts', 'locked_until'
        ]
        read_only_fields = ['id', 'failed_login_attempts', 'locked_until']

    def get_profile_id(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.id
        return None


class UserManagementSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_locked = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    employee_code = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'role_display',
            'raw_password',
            'is_active', 'is_locked', 'failed_login_attempts',
            'locked_until', 'last_login', 'date_joined',
            'employee_id', 'employee_code', 'employee_name', 'department'
        ]
        read_only_fields = ['id', 'raw_password', 'last_login', 'date_joined', 'locked_until']

    def get_is_locked(self, obj):
        return obj.is_locked()

    def get_employee_id(self, obj):
        return obj.profile.id if hasattr(obj, 'profile') and obj.profile else None

    def get_employee_code(self, obj):
        return obj.profile.employee_code if hasattr(obj, 'profile') and obj.profile else None

    def get_employee_name(self, obj):
        return obj.profile.full_name if hasattr(obj, 'profile') and obj.profile else None

    def get_department(self, obj):
        return obj.profile.department if hasattr(obj, 'profile') and obj.profile else None



class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class QuickSwitchRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

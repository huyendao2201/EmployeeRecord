import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_contract_file(file):
    """
    QĐ2: Xác thực tệp đính kèm an toàn:
    - Chỉ cho phép các định dạng tài liệu hợp đồng hợp lệ (.pdf, .doc, .docx, .png, .jpg, .jpeg)
    - Chặn đứng các tệp thực thi / script độc hại (.exe, .sh, .py, .php, .js, .html)
    - Giới hạn kích thước tối đa 10MB
    """
    valid_extensions = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f"Định dạng tệp '{ext}' không được hỗ trợ. Vui lòng chỉ tải lên tệp văn bản hợp đồng (.pdf, .doc, .docx) hoặc hình ảnh (.png, .jpg).")
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError("Dung lượng tệp đính kèm vượt quá giới hạn tối đa cho phép (10MB).")


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    employee_code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    identity_card = models.CharField(max_length=20)  # Số CCCD/CMND
    address = models.TextField(blank=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary_coefficient = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=10000000)
    bank_account = models.CharField(max_length=30, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_code} - {self.full_name} ({self.department})"


class ContractType(models.TextChoices):
    PROBATION = 'PROBATION', 'Thử việc (2 tháng)'
    ONE_YEAR = 'ONE_YEAR', 'Xác định thời hạn (1 năm)'
    THREE_YEAR = 'THREE_YEAR', 'Xác định thời hạn (3 năm)'
    INDEFINITE = 'INDEFINITE', 'Không xác định thời hạn'


class ContractStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Hiệu lực'
    EXPIRED = 'EXPIRED', 'Hết hạn'
    TERMINATED = 'TERMINATED', 'Đã chấm dứt'


class LaborContract(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='contracts'
    )
    contract_number = models.CharField(max_length=50, unique=True)
    contract_type = models.CharField(
        max_length=30,
        choices=ContractType.choices,
        default=ContractType.ONE_YEAR
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    salary_rate = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=ContractStatus.choices,
        default=ContractStatus.ACTIVE
    )
    contract_file = models.FileField(
        upload_to='contracts/%Y/%m/',
        null=True,
        blank=True,
        validators=[validate_contract_file]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"HĐ {self.contract_number} - {self.employee.full_name}"


class AuditLogAction(models.TextChoices):
    LOGIN_SUCCESS = 'LOGIN_SUCCESS', 'Đăng nhập thành công'
    LOGIN_FAILED = 'LOGIN_FAILED', 'Đăng nhập thất bại'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED', 'Tài khoản bị khóa (Brute-force)'
    IDOR_ATTEMPT = 'IDOR_ATTEMPT', 'Phát hiện hành vi IDOR (Truy cập trái phép)'
    VIEW_PROFILE = 'VIEW_PROFILE', 'Xem hồ sơ nhân viên'
    CREATE_PROFILE = 'CREATE_PROFILE', 'Thêm mới hồ sơ nhân viên'
    UPDATE_PROFILE = 'UPDATE_PROFILE', 'Cập nhật hồ sơ nhân viên'
    DELETE_PROFILE = 'DELETE_PROFILE', 'Xóa hồ sơ nhân viên'
    VIEW_CONTRACT = 'VIEW_CONTRACT', 'Xem hợp đồng lao động'
    UPDATE_CONTRACT = 'UPDATE_CONTRACT', 'Cập nhật hợp đồng lao động'
    VIEW_SALARY = 'VIEW_SALARY', 'Truy vấn bảng lương'
    SYSTEM_CONFIG = 'SYSTEM_CONFIG', 'Thay đổi cấu hình hệ thống'


class AuditLogStatus(models.TextChoices):
    SUCCESS = 'SUCCESS', 'Thành công (200)'
    FORBIDDEN = 'FORBIDDEN', 'Bị từ chối (403)'
    WARNING = 'WARNING', 'Cảnh báo (429/400)'
    FAILED = 'FAILED', 'Thất bại'


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    username_attempt = models.CharField(max_length=150, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(
        max_length=50,
        choices=AuditLogAction.choices
    )
    resource_type = models.CharField(max_length=50, blank=True)
    resource_id = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AuditLogStatus.choices,
        default=AuditLogStatus.SUCCESS
    )
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.action} - {self.status}"

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Quản trị viên (Admin)'
    HR = 'HR', 'Quản lý Nhân sự (HR)'
    ACCOUNTANT = 'ACCOUNTANT', 'Kế toán (Accountant)'
    EMPLOYEE = 'EMPLOYEE', 'Nhân viên (Employee)'


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE
    )
    raw_password = models.CharField(
        max_length=128,
        default='Employee@123',
        blank=True,
        help_text="Mật khẩu hiển thị cho Quản trị viên/HR quản lý và cấp phát tài khoản"
    )
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        super().set_password(raw_password)
        if raw_password:
            self.raw_password = raw_password

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def increment_failed_attempts(self, max_attempts=5, lock_minutes=5):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lock_minutes)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

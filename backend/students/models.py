from django.db import models
from django.conf import settings


class Gender(models.TextChoices):
    MALE = 'MALE', 'Nam'
    FEMALE = 'FEMALE', 'Nữ'
    OTHER = 'OTHER', 'Khác'


class StudentStatus(models.TextChoices):
    ENROLLED = 'ENROLLED', 'Đang học'
    ON_LEAVE = 'ON_LEAVE', 'Bảo lưu'
    SUSPENDED = 'SUSPENDED', 'Đình chỉ'
    GRADUATED = 'GRADUATED', 'Đã tốt nghiệp'
    EXPELLED = 'EXPELLED', 'Thôi học'


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_profile'
    )
    student_code = models.CharField(max_length=20, unique=True, verbose_name="Mã số sinh viên (MSSV)")
    full_name = models.CharField(max_length=150, verbose_name="Họ và tên")
    dob = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE, verbose_name="Giới tính")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(verbose_name="Email sinh viên")
    identity_card = models.CharField(max_length=20, verbose_name="Số CCCD/Định danh")
    address = models.TextField(blank=True, verbose_name="Địa chỉ thường trú")
    faculty = models.CharField(max_length=100, verbose_name="Khoa")
    major = models.CharField(max_length=100, verbose_name="Chuyên ngành")
    class_name = models.CharField(max_length=50, verbose_name="Lớp sinh hoạt")
    academic_year = models.CharField(max_length=20, default="2021-2025", verbose_name="Niên khóa")
    status = models.CharField(
        max_length=20,
        choices=StudentStatus.choices,
        default=StudentStatus.ENROLLED,
        verbose_name="Trạng thái học tập"
    )
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=3.20, verbose_name="Điểm GPA tích lũy")
    credits_accumulated = models.PositiveIntegerField(default=68, verbose_name="Tín chỉ tích lũy")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_code} - {self.full_name} ({self.class_name})"


class AcademicRecord(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    course_code = models.CharField(max_length=20, verbose_name="Mã học phần")
    course_name = models.CharField(max_length=150, verbose_name="Tên môn học")
    semester = models.CharField(max_length=50, verbose_name="Học kỳ")
    credits = models.PositiveIntegerField(default=3, verbose_name="Số tín chỉ")
    attendance_score = models.DecimalField(max_digits=4, decimal_places=1, default=10.0, verbose_name="Điểm chuyên cần")
    midterm_score = models.DecimalField(max_digits=4, decimal_places=1, default=8.0, verbose_name="Điểm giữa kỳ")
    final_score = models.DecimalField(max_digits=4, decimal_places=1, default=8.5, verbose_name="Điểm thi kết thúc")
    total_score = models.DecimalField(max_digits=4, decimal_places=1, default=8.6, verbose_name="Điểm tổng kết (hệ 10)")
    letter_grade = models.CharField(max_length=5, default='A', verbose_name="Điểm chữ")
    status = models.CharField(max_length=20, default='PASSED', verbose_name="Trạng thái môn học")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_grade(self):
        # 10% chuyên cần + 30% giữa kỳ + 60% cuối kỳ
        total = (float(self.attendance_score) * 0.1) + (float(self.midterm_score) * 0.3) + (float(self.final_score) * 0.6)
        self.total_score = round(total, 1)
        if self.total_score >= 8.5:
            self.letter_grade = 'A'
        elif self.total_score >= 8.0:
            self.letter_grade = 'B+'
        elif self.total_score >= 7.0:
            self.letter_grade = 'B'
        elif self.total_score >= 6.5:
            self.letter_grade = 'C+'
        elif self.total_score >= 5.5:
            self.letter_grade = 'C'
        elif self.total_score >= 5.0:
            self.letter_grade = 'D+'
        elif self.total_score >= 4.0:
            self.letter_grade = 'D'
        else:
            self.letter_grade = 'F'
        self.status = 'PASSED' if self.total_score >= 4.0 else 'FAILED'

    def save(self, *args, **kwargs):
        self.calculate_grade()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_code}: {self.course_name} ({self.student.student_code}) - {self.letter_grade}"


class AuditLogAction(models.TextChoices):
    LOGIN_SUCCESS = 'LOGIN_SUCCESS', 'Đăng nhập thành công'
    LOGIN_FAILED = 'LOGIN_FAILED', 'Đăng nhập thất bại'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED', 'Tài khoản bị khóa (Brute-force)'
    IDOR_ATTEMPT = 'IDOR_ATTEMPT', 'Phát hiện hành vi IDOR (Truy cập trái phép)'
    VIEW_STUDENT = 'VIEW_STUDENT', 'Xem hồ sơ sinh viên'
    CREATE_STUDENT = 'CREATE_STUDENT', 'Thêm mới sinh viên'
    UPDATE_STUDENT = 'UPDATE_STUDENT', 'Cập nhật hồ sơ sinh viên'
    DELETE_STUDENT = 'DELETE_STUDENT', 'Xóa hồ sơ sinh viên'
    UPDATE_GRADE = 'UPDATE_GRADE', 'Cập nhật điểm học phần'
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
    action = models.CharField(max_length=50, choices=AuditLogAction.choices)
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
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        user_str = self.user.username if self.user else (self.username_attempt or 'Anonymous')
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {user_str} - {self.action} ({self.status})"

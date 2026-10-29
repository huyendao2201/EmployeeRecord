from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import (
    StudentProfile,
    AcademicRecord,
    AuditLog,
    AuditLogAction,
    AuditLogStatus
)
from .serializers import (
    StudentProfileSerializer,
    AcademicRecordSerializer,
    AuditLogSerializer
)
from .permissions import (
    IsOwnerOrRegistrar,
    ReadOnlyAuditLogPermission,
    get_client_ip
)

User = get_user_model()


class StudentProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD Quản lý Hồ sơ Sinh viên đầy đủ tính năng:
    - Tìm kiếm theo MSSV, Họ tên, CCCD
    - Lọc theo Khoa, Lớp, Trạng thái học vụ
    - Phân quyền Object-Level Permission triệt tiêu IDOR
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrRegistrar]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return StudentProfile.objects.none()

        # Quan trọng cho QĐ1: Với các thao tác chi tiết (retrieve, update, delete),
        # cho phép DRF lấy bản ghi mục tiêu để check_object_permissions có thể
        # thẩm định và kích hoạt chặn đứng IDOR (403 Forbidden) thay vì 404.
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return StudentProfile.objects.all()

        # Thao tác danh sách (list):
        if user.role in ['ADMIN', 'REGISTRAR', 'TEACHER']:
            qs = StudentProfile.objects.all().order_by('student_code')

            # Bộ lọc Khoa
            faculty = self.request.query_params.get('faculty')
            if faculty:
                qs = qs.filter(faculty__iexact=faculty)

            # Bộ lọc Lớp
            class_name = self.request.query_params.get('class_name')
            if class_name:
                qs = qs.filter(class_name__iexact=class_name)

            # Bộ lọc Trạng thái
            status_param = self.request.query_params.get('status')
            if status_param:
                qs = qs.filter(status=status_param)

            # Tìm kiếm từ khóa (MSSV, Họ tên, CCCD)
            search = self.request.query_params.get('search')
            if search:
                qs = qs.filter(
                    Q(student_code__icontains=search) |
                    Q(full_name__icontains=search) |
                    Q(identity_card__icontains=search) |
                    Q(email__icontains=search)
                )
            return qs

        # Sinh viên thông thường: Chỉ thấy hồ sơ của chính mình trong danh sách
        return StudentProfile.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        AuditLog.objects.create(
            user=request.user,
            username_attempt=request.user.username,
            ip_address=get_client_ip(request),
            action=AuditLogAction.VIEW_STUDENT,
            resource_type='StudentProfile',
            resource_id=str(instance.id),
            status=AuditLogStatus.SUCCESS,
            details=f"Xem thông tin hồ sơ sinh viên '{instance.full_name}' (MSSV: {instance.student_code})."
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        student = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            username_attempt=self.request.user.username,
            ip_address=get_client_ip(self.request),
            action=AuditLogAction.CREATE_STUDENT,
            resource_type='StudentProfile',
            resource_id=str(student.id),
            status=AuditLogStatus.SUCCESS,
            details=f"Giáo vụ '{self.request.user.username}' đã tạo mới hồ sơ sinh viên: {student.full_name} (MSSV: {student.student_code} - Lớp: {student.class_name})"
        )

    def perform_update(self, serializer):
        student = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            username_attempt=self.request.user.username,
            ip_address=get_client_ip(self.request),
            action=AuditLogAction.UPDATE_STUDENT,
            resource_type='StudentProfile',
            resource_id=str(student.id),
            status=AuditLogStatus.SUCCESS,
            details=f"Người dùng '{self.request.user.username}' (Vai trò: {self.request.user.role}) đã cập nhật thành công hồ sơ sinh viên: {student.full_name} (MSSV: {student.student_code})"
        )

    def perform_destroy(self, instance):
        student_id = instance.id
        student_info = f"{instance.full_name} ({instance.student_code})"
        instance.delete()
        AuditLog.objects.create(
            user=self.request.user,
            username_attempt=self.request.user.username,
            ip_address=get_client_ip(self.request),
            action=AuditLogAction.DELETE_STUDENT,
            resource_type='StudentProfile',
            resource_id=str(student_id),
            status=AuditLogStatus.SUCCESS,
            details=f"Quản trị viên/Giáo vụ '{self.request.user.username}' đã xóa hồ sơ sinh viên: {student_info}"
        )


class AcademicRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD Quản lý Điểm & Học bạ môn học:
    - Sinh viên chỉ được xem điểm của chính mình
    - Giảng viên & Giáo vụ có quyền nhập/cập nhật điểm môn học
    - Chống IDOR trên bản ghi điểm số với IsOwnerOrRegistrar
    """
    serializer_class = AcademicRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrRegistrar]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return AcademicRecord.objects.none()

        # Quan trọng cho QĐ1: Cho phép tìm kiếm đối tượng để check_object_permissions chặn IDOR 403
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return AcademicRecord.objects.all().select_related('student__user')

        student_id = self.request.query_params.get('student_id')
        semester = self.request.query_params.get('semester')

        if user.role in ['ADMIN', 'REGISTRAR', 'TEACHER']:
            qs = AcademicRecord.objects.all().select_related('student')
            if student_id:
                qs = qs.filter(student_id=student_id)
            if semester:
                qs = qs.filter(semester=semester)
            return qs

        # Sinh viên: Chỉ được xem điểm của CHÍNH MÌNH trong danh sách
        qs = AcademicRecord.objects.filter(student__user=user).select_related('student')
        if semester:
            qs = qs.filter(semester=semester)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role not in ['ADMIN', 'REGISTRAR', 'TEACHER']:
            raise permissions.PermissionDenied("Sinh viên không có quyền tự tạo bản ghi điểm số!")
        record = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            username_attempt=self.request.user.username,
            ip_address=get_client_ip(self.request),
            action=AuditLogAction.UPDATE_GRADE,
            resource_type='AcademicRecord',
            resource_id=str(record.id),
            status=AuditLogStatus.SUCCESS,
            details=f"Giảng viên '{self.request.user.username}' đã nhập điểm môn {record.course_name} cho sinh viên {record.student.student_code} (Tổng kết: {record.total_score} - Điểm: {record.letter_grade})"
        )

    def perform_update(self, serializer):
        if self.request.user.role not in ['ADMIN', 'REGISTRAR', 'TEACHER']:
            raise permissions.PermissionDenied("Sinh viên không có quyền tự sửa điểm số!")
        record = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            username_attempt=self.request.user.username,
            ip_address=get_client_ip(self.request),
            action=AuditLogAction.UPDATE_GRADE,
            resource_type='AcademicRecord',
            resource_id=str(record.id),
            status=AuditLogStatus.SUCCESS,
            details=f"Cập nhật điểm môn {record.course_name} cho sinh viên {record.student.student_code} thành: {record.total_score} ({record.letter_grade})"
        )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    QĐ4: Giám sát toàn vẹn Audit Log bất biến (WORM).
    Không hỗ trợ POST, PUT, PATCH, DELETE.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnlyAuditLogPermission]


class SecurityStatsAPIView(APIView):
    """
    API cung cấp dữ liệu số liệu giám sát an ninh và quản trị học vụ.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_students = StudentProfile.objects.count()
        total_grades = AcademicRecord.objects.count()
        idor_attempts = AuditLog.objects.filter(action=AuditLogAction.IDOR_ATTEMPT).count()
        locked_accounts = User.objects.filter(locked_until__isnull=False).count()
        failed_logins = AuditLog.objects.filter(action=AuditLogAction.LOGIN_FAILED).count()
        total_logs = AuditLog.objects.count()

        # Thống kê khoa
        faculties_count = StudentProfile.objects.values('faculty').distinct().count()

        return Response({
            'total_students': total_students,
            'total_grades': total_grades,
            'faculties_count': faculties_count,
            'idor_attempts': idor_attempts,
            'locked_accounts': locked_accounts,
            'failed_logins': failed_logins,
            'total_logs': total_logs,
            'user_role': request.user.role,
            'current_user': request.user.username
        })

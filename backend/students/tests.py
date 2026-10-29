from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, UserRole
from students.models import (
    StudentProfile,
    Gender,
    StudentStatus,
    AcademicRecord,
    AuditLog,
    AuditLogAction,
    AuditLogStatus
)


class StudentSecurityComprehensiveTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Tạo các tài khoản người dùng
        self.admin = User.objects.create_user(
            username='admin',
            password='Admin@123',
            role=UserRole.ADMIN,
            first_name='Admin'
        )

        self.registrar = User.objects.create_user(
            username='giao_vu',
            password='Giaovu@123',
            role=UserRole.REGISTRAR,
            first_name='Giáo vụ Lan'
        )

        self.teacher = User.objects.create_user(
            username='giang_vien',
            password='Gv@123',
            role=UserRole.TEACHER,
            first_name='Giảng viên Minh'
        )

        self.student_nam = User.objects.create_user(
            username='sv_nam',
            password='Pass@123',
            role=UserRole.STUDENT,
            first_name='Lê Văn Nam'
        )

        self.student_huong = User.objects.create_user(
            username='sv_huong',
            password='Pass@123',
            role=UserRole.STUDENT,
            first_name='Phạm Thu Hương'
        )

        # 2. Tạo hồ sơ sinh viên
        self.profile_nam = StudentProfile.objects.create(
            user=self.student_nam,
            student_code='B21DCCN001',
            full_name='Lê Văn Nam',
            gender=Gender.MALE,
            phone='0912345678',
            email='nam.le@student.edu.vn',
            identity_card='001203008899',
            faculty='Công nghệ thông tin',
            major='Kỹ thuật phần mềm',
            class_name='D21CQCN01-B',
            gpa=3.45,
            credits_accumulated=72
        )

        self.profile_huong = StudentProfile.objects.create(
            user=self.student_huong,
            student_code='B21DCCN002',
            full_name='Phạm Thu Hương',
            gender=Gender.FEMALE,
            phone='0987654321',
            email='huong.pham@student.edu.vn',
            identity_card='001203007788',
            faculty='Công nghệ thông tin',
            major='An toàn thông tin',
            class_name='D21CQCN01-B',
            gpa=3.82,
            credits_accumulated=76
        )

        # 3. Tạo điểm môn học
        self.grade_nam = AcademicRecord.objects.create(
            student=self.profile_nam,
            course_code='INT1332',
            course_name='An toàn và Bảo mật Hệ thống',
            semester='Học kỳ 1 - 2024-2025',
            credits=3,
            attendance_score=10.0,
            midterm_score=8.0,
            final_score=8.5
        )

        self.grade_huong = AcademicRecord.objects.create(
            student=self.profile_huong,
            course_code='INT1332',
            course_name='An toàn và Bảo mật Hệ thống',
            semester='Học kỳ 1 - 2024-2025',
            credits=3,
            attendance_score=10.0,
            midterm_score=9.5,
            final_score=9.5
        )

    # ==========================================
    # TEST QĐ1: PHÂN QUYỀN CẤP ĐỐI TƯỢNG & CHỐNG IDOR
    # ==========================================
    def test_qd1_student_can_view_own_profile(self):
        """Sinh viên Nam xem hồ sơ của chính mình -> HTTP 200 OK."""
        self.client.force_authenticate(user=self.student_nam)
        response = self.client.get(f'/api/students/{self.profile_nam.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_code'], 'B21DCCN001')

    def test_qd1_idor_attempt_blocked_and_logged(self):
        """
        Sinh viên Nam cố tình đổi ID để xem hồ sơ Hương (IDOR)
        -> Bị chặn đứng với HTTP 403 Forbidden và ghi nhận Audit Log IDOR_ATTEMPT.
        """
        self.client.force_authenticate(user=self.student_nam)
        response = self.client.get(f'/api/students/{self.profile_huong.id}/')

        # Kiểm tra máy chủ trả về 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Kiểm tra Audit Log đã ghi nhận sự kiện tấn công IDOR
        idor_log = AuditLog.objects.filter(
            action=AuditLogAction.IDOR_ATTEMPT,
            user=self.student_nam
        ).first()
        self.assertIsNotNone(idor_log)
        self.assertEqual(idor_log.status, AuditLogStatus.FORBIDDEN)
        self.assertEqual(idor_log.resource_id, str(self.profile_huong.id))

    def test_qd1_idor_on_grades_blocked(self):
        """Sinh viên Nam cố tình truy xuất điểm học phần của sinh viên Hương -> Bị chặn 403."""
        self.client.force_authenticate(user=self.student_nam)
        response = self.client.get(f'/api/grades/{self.grade_huong.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_qd1_registrar_can_view_all_profiles(self):
        """Giáo vụ có thẩm quyền xem hồ sơ của mọi sinh viên."""
        self.client.force_authenticate(user=self.registrar)
        res1 = self.client.get(f'/api/students/{self.profile_nam.id}/')
        res2 = self.client.get(f'/api/students/{self.profile_huong.id}/')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    # ==========================================
    # TEST QĐ2: XÁC THỰC DỮ LIỆU & TOÀN VẸN ĐIỂM SỐ
    # ==========================================
    def test_qd2_student_cannot_tamper_gpa(self):
        """Sinh viên không được phép tự điều chỉnh điểm GPA hoặc tín chỉ."""
        self.client.force_authenticate(user=self.student_nam)
        response = self.client.patch(f'/api/students/{self.profile_nam.id}/', {
            'gpa': 4.0,
            'credits_accumulated': 150
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gpa', response.data)

    def test_qd2_grade_scores_range_validation(self):
        """Điểm học phần phải nằm trong thang điểm [0.0 - 10.0]."""
        self.client.force_authenticate(user=self.teacher)
        # Điểm thi không hợp lệ: 15.0
        response = self.client.post('/api/grades/', {
            'student': self.profile_nam.id,
            'course_code': 'INT1405',
            'course_name': 'Mạng máy tính',
            'semester': 'Học kỳ 1 - 2024-2025',
            'credits': 3,
            'attendance_score': 10.0,
            'midterm_score': 8.0,
            'final_score': 15.0
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('final_score', response.data)

    def test_qd2_student_cannot_create_grade(self):
        """Sinh viên không có quyền tự tạo bản ghi điểm số."""
        self.client.force_authenticate(user=self.student_nam)
        response = self.client.post('/api/grades/', {
            'student': self.profile_nam.id,
            'course_code': 'INT1405',
            'course_name': 'Mạng máy tính',
            'semester': 'Học kỳ 1 - 2024-2025',
            'credits': 3,
            'attendance_score': 10.0,
            'midterm_score': 10.0,
            'final_score': 10.0
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==========================================
    # TEST QĐ3: PHÒNG THỦ BRUTE-FORCE & KHÓA TÀI KHOẢN
    # ==========================================
    def test_qd3_brute_force_lockout_after_5_attempts(self):
        """Thử sai mật khẩu 5 lần -> Kích hoạt khóa tài khoản 5 phút và trả về HTTP 429."""
        for attempt in range(1, 5):
            res = self.client.post('/api/auth/login/', {
                'username': 'sv_nam',
                'password': 'WrongPassword'
            })
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertFalse(res.data['is_locked'])

        # Lần thứ 5: Khóa tài khoản
        res5 = self.client.post('/api/auth/login/', {
            'username': 'sv_nam',
            'password': 'WrongPassword'
        })
        self.assertEqual(res5.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertTrue(res5.data['is_locked'])

        # Kiểm tra tài khoản trong database
        self.student_nam.refresh_from_db()
        self.assertTrue(self.student_nam.is_locked())

    # ==========================================
    # TEST QĐ4: TÍNH BẤT BIẾN CỦA AUDIT LOG (WORM)
    # ==========================================
    def test_qd4_audit_log_cannot_be_modified_or_deleted(self):
        """API Audit Log chỉ cho phép đọc, cấm mọi thao tác ghi/sửa/xóa (POST, PUT, DELETE)."""
        log_entry = AuditLog.objects.create(
            user=self.admin,
            action=AuditLogAction.SYSTEM_CONFIG,
            status=AuditLogStatus.SUCCESS,
            details="Test log"
        )
        self.client.force_authenticate(user=self.admin)

        # Cấm POST
        res_post = self.client.post('/api/audit-logs/', {'action': 'FAKE'})
        self.assertIn(res_post.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])

        # Cấm DELETE
        res_del = self.client.delete(f'/api/audit-logs/{log_entry.id}/')
        self.assertIn(res_del.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])

    def test_qd4_student_cannot_view_audit_logs(self):
        """Sinh viên không có quyền xem Audit Log bảo mật hệ thống."""
        self.client.force_authenticate(user=self.student_nam)
        response = self.client.get('/api/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

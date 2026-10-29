from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, UserRole
from employees.models import (
    EmployeeProfile,
    LaborContract,
    AuditLog,
    AuditLogAction,
    AuditLogStatus
)


class SecurityAndAccessControlTestCase(TestCase):
    """
    Bộ kiểm thử an ninh tự động kiểm chứng 4 Quyết định Thiết kế (QĐ1 - QĐ4):
    1. Chống IDOR (Insecure Direct Object Reference)
    2. Chống giả mạo dữ liệu lương nhạy cảm
    3. Phòng thủ tấn công Brute-force và khóa tài khoản
    4. Tính toàn vẹn (Immutability) của Audit Log
    """

    def setUp(self):
        self.client = APIClient()

        # Tạo người dùng các vai trò
        self.user_emp_a = User.objects.create_user(
            username='emp_a', password='Password@123', role=UserRole.EMPLOYEE
        )
        self.user_emp_b = User.objects.create_user(
            username='emp_b', password='Password@123', role=UserRole.EMPLOYEE
        )
        self.user_hr = User.objects.create_user(
            username='hr_user', password='Password@123', role=UserRole.HR
        )
        self.user_admin = User.objects.create_user(
            username='admin_user', password='Password@123', role=UserRole.ADMIN
        )

        # Tạo hồ sơ nhân viên
        self.profile_a = EmployeeProfile.objects.create(
            user=self.user_emp_a,
            employee_code='EMP001',
            full_name='Nhân viên A',
            phone='0912345678',
            identity_card='001196001111',
            department='Kỹ thuật',
            position='Kỹ sư',
            basic_salary=15000000
        )
        self.profile_b = EmployeeProfile.objects.create(
            user=self.user_emp_b,
            employee_code='EMP002',
            full_name='Nhân viên B',
            phone='0987654321',
            identity_card='001198002222',
            department='Kinh doanh',
            position='Chuyên viên',
            basic_salary=18000000
        )

    def get_token_for(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_idor_defense_employee_cannot_access_other_profile(self):
        """
        QĐ1: Chứng minh Đăng nhập thành công KHÔNG CÓ NGHĨA là được xem hồ sơ người khác.
        Nhân viên A cố tình thay đổi ID trên URL/API để lấy hồ sơ B -> Phải bị chặn 403 Forbidden!
        """
        token_a = self.get_token_for(self.user_emp_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')

        # 1. Nhân viên A truy cập hồ sơ chính mình -> Thành công (200 OK)
        res_own = self.client.get(f'/api/employees/{self.profile_a.id}/')
        self.assertEqual(res_own.status_code, status.HTTP_200_OK)
        self.assertEqual(res_own.data['employee_code'], 'EMP001')

        # 2. Nhân viên A cố tình sửa ID thành profile_b.id -> Bị chặn (403 Forbidden)
        res_idor = self.client.get(f'/api/employees/{self.profile_b.id}/')
        self.assertEqual(res_idor.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Kiểm chứng Audit Log đã ghi nhận hành vi IDOR
        log = AuditLog.objects.filter(action=AuditLogAction.IDOR_ATTEMPT).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, AuditLogStatus.FORBIDDEN)
        self.assertIn("cố tình truy cập trái phép", log.details)

    def test_hr_can_access_all_profiles(self):
        """HR có thẩm quyền hợp lệ để xem hồ sơ của bất kỳ nhân viên nào."""
        token_hr = self.get_token_for(self.user_hr)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_hr}')

        res_a = self.client.get(f'/api/employees/{self.profile_a.id}/')
        res_b = self.client.get(f'/api/employees/{self.profile_b.id}/')
        self.assertEqual(res_a.status_code, status.HTTP_200_OK)
        self.assertEqual(res_b.status_code, status.HTTP_200_OK)

    def test_employee_cannot_tamper_salary(self):
        """
        QĐ2: Nhân viên không thể gửi request sửa trường nhạy cảm (lương) của mình.
        """
        token_a = self.get_token_for(self.user_emp_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')

        # Thử nâng lương từ 15tr lên 99tr
        res = self.client.patch(
            f'/api/employees/{self.profile_a.id}/',
            {'basic_salary': 99000000},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('security_violation', res.data)

    def test_brute_force_account_lockout(self):
        """
        QĐ3: Thử nhập sai mật khẩu 5 lần -> Tài khoản phải bị khóa và trả 429 Too Many Requests.
        """
        for i in range(4):
            res = self.client.post('/api/auth/login/', {
                'username': 'emp_a',
                'password': 'WrongPassword!'
            })
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertFalse(res.data['is_locked'])

        # Lần thứ 5 sai -> Khóa tài khoản
        res_5 = self.client.post('/api/auth/login/', {
            'username': 'emp_a',
            'password': 'WrongPassword!'
        })
        self.assertEqual(res_5.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertTrue(res_5.data['is_locked'])

        # Kiểm chứng trong AuditLog có ghi nhận ACCOUNT_LOCKED
        lock_log = AuditLog.objects.filter(action=AuditLogAction.ACCOUNT_LOCKED).first()
        self.assertIsNotNone(lock_log)

    def test_audit_log_immutability(self):
        """
        QĐ4: Tính bất biến của nhật ký: Cấm POST, PUT, DELETE vào bảng Audit Log qua API.
        """
        token_admin = self.get_token_for(self.user_admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_admin}')

        # Admin được phép đọc log
        res_read = self.client.get('/api/audit-logs/')
        self.assertEqual(res_read.status_code, status.HTTP_200_OK)

        # Cố tình POST tạo log giả mạo -> Bị chặn (403 Forbidden hoặc 405 Method Not Allowed)
        res_post = self.client.post('/api/audit-logs/', {'action': 'FAKE_LOG'})
        self.assertIn(res_post.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])

    def test_input_validation_invalid_phone_and_cccd_rejected(self):
        """
        QĐ2: Kiểm tra và xác thực dữ liệu đầu vào.
        Người dùng gửi dữ liệu sai định dạng (số điện thoại ngắn/chứa chữ) hoặc
        cố tình chèn mã độc (SQLi/XSS vào CCCD) -> Bị từ chối HTTP 400 Bad Request.
        """
        token_a = self.get_token_for(self.user_emp_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')

        # 1. Thử gửi số điện thoại không hợp lệ (ít số hoặc chứa ký tự)
        res_phone = self.client.patch(
            f'/api/employees/{self.profile_a.id}/',
            {'phone': '0912invalid'},
            format='json'
        )
        self.assertEqual(res_phone.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', res_phone.data)

        # 2. Thử chèn payload độc hại vào CCCD (SQL Injection / XSS attempt)
        res_cccd = self.client.patch(
            f'/api/employees/{self.profile_a.id}/',
            {'identity_card': "001' OR '1'='1"},
            format='json'
        )
        self.assertEqual(res_cccd.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('identity_card', res_cccd.data)

    def test_profile_update_creates_audit_log(self):
        """
        QĐ4: Thực hiện một thao tác cập nhật hồ sơ và kiểm tra nhật ký được tạo ra.
        """
        token_a = self.get_token_for(self.user_emp_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')

        # Thực hiện cập nhật địa chỉ hợp lệ
        res = self.client.patch(
            f'/api/employees/{self.profile_a.id}/',
            {'address': '123 Đường Nguyễn Huệ, Quận 1, TP.HCM'},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Kiểm chứng nhật ký đã ghi nhận hành động UPDATE_PROFILE thành công
        update_log = AuditLog.objects.filter(
            action=AuditLogAction.UPDATE_PROFILE,
            resource_id=str(self.profile_a.id)
        ).first()
        self.assertIsNotNone(update_log)
        self.assertEqual(update_log.status, AuditLogStatus.SUCCESS)
        self.assertEqual(update_log.user, self.user_emp_a)
        self.assertIn('Cập nhật thành công thông tin hồ sơ', update_log.details)

    def test_contract_file_upload_validation_and_access_control(self):
        """
        Kiểm thử lưu trữ tệp hợp đồng lao động:
        1. QĐ2: Chặn tệp thực thi độc hại (.exe, script)
        2. Chấp nhận tệp hợp đồng an toàn (.pdf, .docx, .png, .jpg)
        3. QĐ1: Nhân viên chỉ tải được tệp của mình, cố tình đổi ID để tải tệp người khác bị chặn 403 (IDOR)
        """
        from django.core.files.uploadedfile import SimpleUploadedFile
        from datetime import date

        # Tạo hợp đồng ban đầu cho A và B
        contract_a = LaborContract.objects.create(
            employee=self.profile_a,
            contract_number="HDLD-A-001",
            start_date=date.today(),
            salary_rate=15000000
        )
        contract_b = LaborContract.objects.create(
            employee=self.profile_b,
            contract_number="HDLD-B-002",
            start_date=date.today(),
            salary_rate=18000000
        )

        token_hr = self.get_token_for(self.user_hr)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_hr}')

        # 1. HR thử tải lên tệp độc hại (.exe) -> Bị chặn 400 Bad Request
        malicious_file = SimpleUploadedFile("virus.exe", b"MZ_binary_executable_code", content_type="application/octet-stream")
        res_bad = self.client.patch(
            f'/api/contracts/{contract_a.id}/',
            {'contract_file': malicious_file},
            format='multipart'
        )
        self.assertEqual(res_bad.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('contract_file', res_bad.data)

        # 2. HR tải lên tệp hợp đồng PDF hợp lệ -> 200 OK
        valid_pdf = SimpleUploadedFile("hop_dong_chuan.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        res_good = self.client.patch(
            f'/api/contracts/{contract_a.id}/',
            {'contract_file': valid_pdf},
            format='multipart'
        )
        self.assertEqual(res_good.status_code, status.HTTP_200_OK)
        self.assertTrue(res_good.data['contract_file'])

        # 3. Nhân viên A truy cập tải tệp hợp đồng của chính mình -> 200 OK
        token_a = self.get_token_for(self.user_emp_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_a}')
        res_download_own = self.client.get(f'/api/contracts/{contract_a.id}/download/')
        self.assertEqual(res_download_own.status_code, status.HTTP_200_OK)

        # 4. Nhân viên B cố tình truy cập tải tệp hợp đồng của A (IDOR) -> 403 Forbidden!
        token_b = self.get_token_for(self.user_emp_b)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_b}')
        res_download_idor = self.client.get(f'/api/contracts/{contract_a.id}/download/')
        self.assertEqual(res_download_idor.status_code, status.HTTP_403_FORBIDDEN)



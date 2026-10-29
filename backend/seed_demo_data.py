import os
import sys
import django
from datetime import date

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, UserRole
from employees.models import (
    EmployeeProfile,
    LaborContract,
    ContractType,
    ContractStatus,
    AuditLog,
    AuditLogAction,
    AuditLogStatus
)


def seed():
    print("🚀 Bắt đầu khởi tạo dữ liệu mẫu cho Hệ thống Quản lý & Bảo mật Hồ sơ Nhân viên (SecureHR)...")

    # 1. Tạo các tài khoản người dùng
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@securehr.vn',
            'role': UserRole.ADMIN,
            'password': 'Admin@123',
            'first_name': 'Hệ thống',
            'last_name': 'Quản trị viên',
            'is_superuser': True,
            'is_staff': True
        },
        {
            'username': 'hr_linh',
            'email': 'linh.nguyen@securehr.vn',
            'role': UserRole.HR,
            'password': 'Hr@123',
            'first_name': 'Linh',
            'last_name': 'Nguyễn Thị Mỹ (Trưởng phòng HR)',
            'is_staff': True
        },
        {
            'username': 'ketoan_hoa',
            'email': 'hoa.tran@securehr.vn',
            'role': UserRole.ACCOUNTANT,
            'password': 'Ketoan@123',
            'first_name': 'Hoa',
            'last_name': 'Trần Thanh (Kế toán trưởng)',
            'is_staff': False
        },
        {
            'username': 'nv_nam',
            'email': 'nam.nguyen@securehr.vn',
            'role': UserRole.EMPLOYEE,
            'password': 'Employee@123',
            'first_name': 'Nam',
            'last_name': 'Nguyễn Văn (Nhân viên A)',
            'is_staff': False
        },
        {
            'username': 'nv_huong',
            'email': 'huong.pham@securehr.vn',
            'role': UserRole.EMPLOYEE,
            'password': 'Employee@123',
            'first_name': 'Hương',
            'last_name': 'Phạm Thu (Nhân viên B)',
            'is_staff': False
        },
        {
            'username': 'nv_tuan',
            'email': 'tuan.le@securehr.vn',
            'role': UserRole.EMPLOYEE,
            'password': 'Employee@123',
            'first_name': 'Tuấn',
            'last_name': 'Lê Anh (Nhân viên C)',
            'is_staff': False
        }
    ]

    users_map = {}
    for udata in users_data:
        user, created = User.objects.get_or_create(
            username=udata['username'],
            defaults={
                'email': udata['email'],
                'role': udata['role'],
                'first_name': udata['first_name'],
                'last_name': udata['last_name'],
                'is_superuser': udata.get('is_superuser', False),
                'is_staff': udata.get('is_staff', False),
            }
        )
        user.set_password(udata['password'])
        user.raw_password = udata['password']
        user.role = udata['role']
        user.first_name = udata['first_name']
        user.last_name = udata['last_name']
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        users_map[udata['username']] = user
        status_txt = "Tạo mới" if created else "Cập nhật"
        print(f"  [+] {status_txt} tài khoản: {user.username} (Role: {user.role})")

    # 2. Tạo Hồ sơ nhân viên (EmployeeProfile)
    profiles_data = [
        {
            'user': users_map['nv_nam'],
            'employee_code': 'EMP001',
            'full_name': 'Nguyễn Văn Nam',
            'dob': date(1996, 5, 14),
            'phone': '0912345678',
            'email': 'nam.nguyen@securehr.vn',
            'identity_card': '001196001111',
            'address': 'Tầng 8, Tòa nhà Keangnam Landmark, Nam Từ Liêm, Hà Nội',
            'department': 'Phòng Công nghệ & Phần mềm',
            'position': 'Kỹ sư phần mềm cao cấp (Senior Developer)',
            'salary_coefficient': 1.80,
            'basic_salary': 18000000,
            'bank_account': '190366688899',
            'bank_name': 'Techcombank'
        },
        {
            'user': users_map['nv_huong'],
            'employee_code': 'EMP002',
            'full_name': 'Phạm Thu Hương',
            'dob': date(1998, 9, 22),
            'phone': '0987654321',
            'email': 'huong.pham@securehr.vn',
            'identity_card': '001198002222',
            'address': 'Số 45 Đường Hoàng Hoa Thám, Ba Đình, Hà Nội',
            'department': 'Phòng Kinh doanh & Tiếp thị',
            'position': 'Chuyên viên Phát triển Thị trường',
            'salary_coefficient': 1.50,
            'basic_salary': 15000000,
            'bank_account': '101234567890',
            'bank_name': 'Vietcombank'
        },
        {
            'user': users_map['nv_tuan'],
            'employee_code': 'EMP003',
            'full_name': 'Lê Anh Tuấn',
            'dob': date(1994, 11, 3),
            'phone': '0903123456',
            'email': 'tuan.le@securehr.vn',
            'identity_card': '001194003333',
            'address': 'Số 12 ngõ 86 Duy Tân, Cầu Giấy, Hà Nội',
            'department': 'Phòng Công nghệ & Phần mềm',
            'position': 'Trưởng nhóm An ninh thông tin (Security Lead)',
            'salary_coefficient': 2.50,
            'basic_salary': 25000000,
            'bank_account': '039876543210',
            'bank_name': 'MBBank'
        },
        {
            'user': users_map['hr_linh'],
            'employee_code': 'HR001',
            'full_name': 'Nguyễn Thị Mỹ Linh',
            'dob': date(1992, 4, 18),
            'phone': '0978999888',
            'email': 'linh.nguyen@securehr.vn',
            'identity_card': '001192004444',
            'address': 'Số 68 Phố Huế, Hai Bà Trưng, Hà Nội',
            'department': 'Phòng Hành chính - Nhân sự',
            'position': 'Trưởng phòng Nhân sự',
            'salary_coefficient': 2.80,
            'basic_salary': 28000000,
            'bank_account': '190288899900',
            'bank_name': 'Techcombank'
        },
        {
            'user': users_map['ketoan_hoa'],
            'employee_code': 'ACC001',
            'full_name': 'Trần Thanh Hoa',
            'dob': date(1990, 8, 12),
            'phone': '0936123789',
            'email': 'hoa.tran@securehr.vn',
            'identity_card': '001190005555',
            'address': 'Số 25 Láng Hạ, Đống Đa, Hà Nội',
            'department': 'Phòng Tài chính - Kế toán',
            'position': 'Kế toán trưởng',
            'salary_coefficient': 2.60,
            'basic_salary': 26000000,
            'bank_account': '0021000123456',
            'bank_name': 'Vietcombank'
        }
    ]

    profiles_map = {}
    for pdata in profiles_data:
        profile, created = EmployeeProfile.objects.update_or_create(
            user=pdata['user'],
            defaults={
                'employee_code': pdata['employee_code'],
                'full_name': pdata['full_name'],
                'dob': pdata['dob'],
                'phone': pdata['phone'],
                'email': pdata['email'],
                'identity_card': pdata['identity_card'],
                'address': pdata['address'],
                'department': pdata['department'],
                'position': pdata['position'],
                'salary_coefficient': pdata['salary_coefficient'],
                'basic_salary': pdata['basic_salary'],
                'bank_account': pdata['bank_account'],
                'bank_name': pdata['bank_name']
            }
        )
        profiles_map[pdata['employee_code']] = profile
        action = "Tạo mới" if created else "Cập nhật"
        print(f"  [+] {action} hồ sơ nhân viên: {profile.employee_code} - {profile.full_name}")

    # 3. Tạo Hợp đồng lao động (LaborContract)
    contracts_data = [
        {
            'employee': profiles_map['EMP001'],
            'contract_number': 'HĐLĐ-2024-001',
            'contract_type': ContractType.ONE_YEAR,
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'salary_rate': 18000000,
            'status': ContractStatus.ACTIVE,
            'notes': 'Hợp đồng lao động chính thức có đóng BHXH, BHYT theo quy chế công ty.'
        },
        {
            'employee': profiles_map['EMP002'],
            'contract_number': 'HĐLĐ-2024-002',
            'contract_type': ContractType.THREE_YEAR,
            'start_date': date(2023, 6, 1),
            'end_date': date(2026, 5, 31),
            'salary_rate': 15000000,
            'status': ContractStatus.ACTIVE,
            'notes': 'Hợp đồng lao động xác định thời hạn 3 năm kèm cam kết bảo mật NDA.'
        },
        {
            'employee': profiles_map['EMP003'],
            'contract_number': 'HĐLĐ-2023-009',
            'contract_type': ContractType.INDEFINITE,
            'start_date': date(2022, 1, 15),
            'end_date': None,
            'salary_rate': 25000000,
            'status': ContractStatus.ACTIVE,
            'notes': 'Hợp đồng không xác định thời hạn cho vị trí nhân sự nòng cốt.'
        },
        {
            'employee': profiles_map['HR001'],
            'contract_number': 'HĐLĐ-2021-005',
            'contract_type': ContractType.INDEFINITE,
            'start_date': date(2021, 3, 1),
            'end_date': None,
            'salary_rate': 28000000,
            'status': ContractStatus.ACTIVE,
            'notes': 'Hợp đồng quản lý cấp cao phòng Nhân sự.'
        },
        {
            'employee': profiles_map['ACC001'],
            'contract_number': 'HĐLĐ-2020-002',
            'contract_type': ContractType.INDEFINITE,
            'start_date': date(2020, 5, 10),
            'end_date': None,
            'salary_rate': 26000000,
            'status': ContractStatus.ACTIVE,
            'notes': 'Hợp đồng phụ trách tài chính và chữ ký số kế toán.'
        }
    ]

    for cdata in contracts_data:
        contract, created = LaborContract.objects.update_or_create(
            contract_number=cdata['contract_number'],
            defaults={
                'employee': cdata['employee'],
                'contract_type': cdata['contract_type'],
                'start_date': cdata['start_date'],
                'end_date': cdata['end_date'],
                'salary_rate': cdata['salary_rate'],
                'status': cdata['status'],
                'notes': cdata['notes']
            }
        )
        action = "Tạo mới" if created else "Cập nhật"
        print(f"  [+] {action} hợp đồng: {contract.contract_number} ({contract.employee.full_name})")

    # 4. Khởi tạo sẵn một số sự kiện Audit Log minh họa
    audit_events = [
        {
            'user': users_map['admin'],
            'action': AuditLogAction.SYSTEM_CONFIG,
            'status': AuditLogStatus.SUCCESS,
            'resource_type': 'System',
            'details': 'Hệ thống SecureHR khởi động và thiết lập ma trận phân quyền Zero-Trust RBAC.'
        },
        {
            'user': users_map['nv_nam'],
            'action': AuditLogAction.LOGIN_SUCCESS,
            'status': AuditLogStatus.SUCCESS,
            'resource_type': 'Auth',
            'details': "Đăng nhập thành công từ IP 127.0.0.1 với vai trò 'Nhân viên (Employee)'."
        },
        {
            'user': users_map['nv_nam'],
            'action': AuditLogAction.IDOR_ATTEMPT,
            'status': AuditLogStatus.FORBIDDEN,
            'resource_type': 'EmployeeProfile',
            'resource_id': str(profiles_map['EMP002'].id),
            'details': f"CẢNH BÁO AN NINH (QĐ1): Người dùng 'nv_nam' cố tình thay đổi ID để truy xuất trái phép hồ sơ của 'EMP002 - Phạm Thu Hương'. Máy chủ đã chặn lại (403 Forbidden)."
        },
        {
            'user': users_map['hr_linh'],
            'action': AuditLogAction.VIEW_PROFILE,
            'status': AuditLogStatus.SUCCESS,
            'resource_type': 'EmployeeProfile',
            'resource_id': str(profiles_map['EMP001'].id),
            'details': "Trưởng phòng HR xem thông tin nhân sự của 'Nguyễn Văn Nam' (EMP001)."
        },
        {
            'user': None,
            'username_attempt': 'attacker_unknown',
            'action': AuditLogAction.ACCOUNT_LOCKED,
            'status': AuditLogStatus.WARNING,
            'resource_type': 'Auth',
            'details': "PHÒNG THỦ BRUTE-FORCE (QĐ3): Phát hiện 5 lần thử sai mật khẩu liên tiếp từ cùng một IP. Khóa tài khoản 5 phút và trả về mã HTTP 429 Too Many Requests."
        }
    ]

    for ev in audit_events:
        AuditLog.objects.create(
            user=ev.get('user'),
            username_attempt=ev.get('username_attempt', ''),
            ip_address='127.0.0.1',
            action=ev['action'],
            status=ev['status'],
            resource_type=ev.get('resource_type', ''),
            resource_id=ev.get('resource_id', ''),
            details=ev['details']
        )
    print("  [+] Đã tạo sẵn 5 bản ghi Audit Log minh họa QĐ1 - QĐ4.")

    print("\n✅ HOÀN TẤT KHỞI TẠO DỮ LIỆU SECUREHR THÀNH CÔNG!")
    print("----------------------------------------------------------------------")
    print("Danh sách tài khoản demo phục vụ thuyết trình 5 phút:")
    print("  1. Quản trị viên:    admin       / Admin@123     (Toàn quyền hệ thống)")
    print("  2. Quản lý Nhân sự:  hr_linh     / Hr@123        (Xem/Sửa toàn bộ hồ sơ NV, Hợp đồng)")
    print("  3. Kế toán:          ketoan_hoa  / Ketoan@123    (Xem lương, hợp đồng, hồ sơ)")
    print("  4. Nhân viên A:      nv_nam      / Employee@123  (Chỉ xem hồ sơ & hợp đồng của chính mình)")
    print("  5. Nhân viên B:      nv_huong    / Employee@123  (Mục tiêu giả lập tấn công IDOR)")
    print("  6. Nhân viên C:      nv_tuan     / Employee@123  (Nhân viên bảo mật)")
    print("----------------------------------------------------------------------")


if __name__ == '__main__':
    seed()

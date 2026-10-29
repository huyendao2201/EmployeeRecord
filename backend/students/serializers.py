import re
from rest_framework import serializers
from .models import StudentProfile, AcademicRecord, AuditLog


class StudentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'username',
            'student_code',
            'full_name',
            'dob',
            'gender',
            'gender_display',
            'phone',
            'email',
            'identity_card',
            'address',
            'faculty',
            'major',
            'class_name',
            'academic_year',
            'status',
            'status_display',
            'gpa',
            'credits_accumulated',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_student_code(self, value):
        if not re.match(r'^[A-Za-z0-9_-]{4,20}$', value):
            raise serializers.ValidationError("Mã số sinh viên (MSSV) chỉ được chứa chữ cái, số và dấu gạch ngang (4-20 ký tự).")
        return value.upper()

    def validate_phone(self, value):
        if not re.match(r'^[0-9+() -]{9,15}$', value):
            raise serializers.ValidationError("Số điện thoại không đúng định dạng chuẩn.")
        return value

    def validate_identity_card(self, value):
        if not re.match(r'^[0-9]{9,12}$', value):
            raise serializers.ValidationError("Số CCCD/Định danh cá nhân phải gồm 9 đến 12 chữ số hợp lệ.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        # QĐ2: Kiểm tra quyền sửa trường dữ liệu nhạy cảm (Field Protection)
        if request and hasattr(request, 'user') and request.user.role == 'STUDENT':
            # Sinh viên cố tình sửa điểm GPA hoặc Tín chỉ tích lũy
            if 'gpa' in attrs:
                raise serializers.ValidationError({
                    'gpa': 'Vi phạm quyền hạn: Sinh viên không có thẩm quyền tự điều chỉnh điểm GPA tích lũy!'
                })
            if 'credits_accumulated' in attrs:
                raise serializers.ValidationError({
                    'credits_accumulated': 'Vi phạm quyền hạn: Sinh viên không được phép thay đổi số tín chỉ tích lũy!'
                })
            if 'status' in attrs:
                raise serializers.ValidationError({
                    'status': 'Sinh viên không được phép tự thay đổi trạng thái học vụ.'
                })
            if 'student_code' in attrs:
                raise serializers.ValidationError({
                    'student_code': 'Mã số sinh viên là định danh bất biến, chỉ Phòng Đào tạo mới có quyền cấp đổi.'
                })
        return attrs


class AcademicRecordSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(source='student.student_code', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = AcademicRecord
        fields = [
            'id',
            'student',
            'student_code',
            'student_name',
            'course_code',
            'course_name',
            'semester',
            'credits',
            'attendance_score',
            'midterm_score',
            'final_score',
            'total_score',
            'letter_grade',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'total_score', 'letter_grade', 'status', 'created_at', 'updated_at']

    def validate_attendance_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Điểm chuyên cần phải nằm trong khoảng từ 0.0 đến 10.0.")
        return value

    def validate_midterm_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Điểm giữa kỳ phải nằm trong khoảng từ 0.0 đến 10.0.")
        return value

    def validate_final_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Điểm thi kết thúc học phần phải nằm trong khoảng từ 0.0 đến 10.0.")
        return value


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'username',
            'username_attempt',
            'ip_address',
            'action',
            'action_display',
            'resource_type',
            'resource_id',
            'status',
            'status_display',
            'details',
            'timestamp'
        ]
        read_only_fields = '__all__'

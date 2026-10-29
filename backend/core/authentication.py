from rest_framework_simplejwt.authentication import JWTAuthentication


class QueryParamJWTAuthentication(JWTAuthentication):
    """
    Hỗ trợ xác thực JWT qua query param ?token=... phục vụ cho việc:
    - Mở xem trực tiếp tệp PDF/ảnh trong tab mới của trình duyệt.
    - Tải xuống tệp đính kèm trực tiếp thông qua liên kết bảo mật có phân quyền.
    Vẫn ưu tiên header Authorization: Bearer <token> nếu có.
    """
    def authenticate(self, request):
        token = request.query_params.get('token')
        if token and 'HTTP_AUTHORIZATION' not in request.META:
            try:
                validated_token = self.get_validated_token(token)
                return self.get_user(validated_token), validated_token
            except Exception:
                return None
        return super().authenticate(request)

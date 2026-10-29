from rest_framework.views import exception_handler
from rest_framework import status

VIETNAMESE_ERROR_TRANSLATIONS = {
    'You do not have permission to perform this action.': 'Bạn không có quyền thực hiện thao tác này (Truy cập bị từ chối).',
    'Authentication credentials were not provided.': 'Vui lòng đăng nhập để thực hiện thao tác này.',
    'Given token not valid for any token type': 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn.',
    'Token is invalid or expired': 'Mã xác thực không hợp lệ hoặc đã hết hạn.',
    'Not found.': 'Không tìm thấy dữ liệu yêu cầu.',
    'Method not allowed.': 'Phương thức yêu cầu không được hỗ trợ.',
    'This field is required.': 'Trường thông tin này là bắt buộc.',
}

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        if isinstance(data, dict):
            if 'detail' in data:
                detail_str = str(data['detail'])
                if detail_str in VIETNAMESE_ERROR_TRANSLATIONS:
                    data['detail'] = VIETNAMESE_ERROR_TRANSLATIONS[detail_str]
                elif response.status_code == status.HTTP_403_FORBIDDEN and 'permission' in detail_str.lower():
                    data['detail'] = 'Bạn không có quyền thực hiện thao tác này (Truy cập bị từ chối).'
            if 'error' in data:
                error_str = str(data['error'])
                if error_str in VIETNAMESE_ERROR_TRANSLATIONS:
                    data['error'] = VIETNAMESE_ERROR_TRANSLATIONS[error_str]
        elif isinstance(data, list):
            new_data = []
            for item in data:
                item_str = str(item)
                new_data.append(VIETNAMESE_ERROR_TRANSLATIONS.get(item_str, item_str))
            response.data = new_data

    return response

from enum import Enum
from typing import Dict, Optional

from fastapi import HTTPException, status


class ErrorCode(int, Enum):
    USER_NOT_FOUND = 10
    DONVI_NOT_FOUND = 20
    INVALID_IMAGE_TYPE = 30
    INVALID_CREDENTIALS = 40
    INVALID_TOKEN = 41
    INSUFFICIENT_PERMISSION = 50
    HEADER_DONVI_REQUIRED = 60


ERROR_DEFINITIONS: Dict[ErrorCode, Dict[str, object]] = {
    ErrorCode.USER_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "User không tồn tại",
    },
    ErrorCode.DONVI_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Đơn vị không tồn tại",
    },
    ErrorCode.INVALID_IMAGE_TYPE: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Chỉ cho phép upload ảnh JPG/PNG",
    },
    ErrorCode.INVALID_CREDENTIALS: {
        "status": status.HTTP_401_UNAUTHORIZED,
        "message": "Thông tin đăng nhập không chính xác",
    },
    ErrorCode.INVALID_TOKEN: {
        "status": status.HTTP_401_UNAUTHORIZED,
        "message": "Token không hợp lệ hoặc đã hết hạn",
    },
    ErrorCode.INSUFFICIENT_PERMISSION: {
        "status": status.HTTP_403_FORBIDDEN,
        "message": "Bạn không có đủ quyền để thực hiện hành động này",
    },
    ErrorCode.HEADER_DONVI_REQUIRED: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Thiếu header X-DonVi-Id",
    },
}


def app_exception(code: ErrorCode, extra_detail: Optional[str] = None) -> None:
    """
    Ném HTTPException dựa trên mã lỗi tập trung.

    - code: mã lỗi nội bộ (ErrorCode)
    - extra_detail: nếu muốn bổ sung chi tiết cụ thể cho lỗi.
    """
    info = ERROR_DEFINITIONS[code]
    base_msg = info["message"]
    detail = f"{base_msg}: {extra_detail}" if extra_detail else base_msg
    raise HTTPException(status_code=info["status"], detail=detail)  # type: ignore[arg-type]


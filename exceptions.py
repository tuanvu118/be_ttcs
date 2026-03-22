from enum import Enum
from typing import Dict, Optional

from fastapi import HTTPException, status


class ErrorCode(int, Enum):
    USER_NOT_FOUND = 10
    UNIT_NOT_FOUND = 20
    INVALID_IMAGE_TYPE = 30

    INVALID_CREDENTIALS = 40
    INVALID_TOKEN = 41

    INSUFFICIENT_PERMISSION = 50
    HEADER_UNIT_REQUIRED = 60

    EVENT_NOT_FOUND = 70
    INVALID_REGISTRATION_TIME = 71
    INVALID_EVENT_TIME = 72
    EVENT_MUST_START_AFTER_REGISTRATION = 73

    REPORT_NOT_FOUND = 80
    REPORT_ALREADY_EXISTS = 81

    REGISTRATION_NOT_FOUND = 90
    ALREADY_REGISTERED = 91

    INVALID_POINT_VALUE = 100
    INVALID_UNIT_EVENT_TYPE_VALUE = 101

    SEMESTER_NOT_FOUND = 110
    ACTIVE_SEMESTER_NOT_FOUND = 111
    INVALID_SEMESTER_TIME = 112
    INVALID_ID_FORMAT = 113

    UNIT_EVENT_NOT_FOUND = 120
    INVALID_UNIT_EVENT_TYPE = 121
    UNIT_EVENT_SUBMISSION_ALREADY_EXISTS = 122
    UNIT_EVENT_SUBMISSION_NOT_FOUND = 123
    UNIT_EVENT_SUBMISSION_ALREADY_APPROVED = 124
    LIST_USER_ID_IS_REQUIRED = 125
    UNIT_NOT_ASSIGNED_TO_EVENT = 126

ERROR_DEFINITIONS: Dict[ErrorCode, Dict[str, object]] = {
    ErrorCode.USER_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "User khong ton tai",
    },
    ErrorCode.UNIT_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Unit khong ton tai",
    },
    ErrorCode.INVALID_IMAGE_TYPE: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Chi cho phep upload anh JPG/PNG",
    },
    ErrorCode.INVALID_CREDENTIALS: {
        "status": status.HTTP_401_UNAUTHORIZED,
        "message": "Thong tin dang nhap khong chinh xac",
    },
    ErrorCode.INVALID_TOKEN: {
        "status": status.HTTP_401_UNAUTHORIZED,
        "message": "Token khong hop le hoac da het han",
    },
    ErrorCode.INSUFFICIENT_PERMISSION: {
        "status": status.HTTP_403_FORBIDDEN,
        "message": "Ban khong co du quyen de thuc hien hanh dong nay",
    },
    ErrorCode.HEADER_UNIT_REQUIRED: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Thieu header X-Unit-Id",
    },
    ErrorCode.EVENT_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Su kien khong ton tai",
    },
    ErrorCode.REPORT_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Bao cao khong ton tai",
    },
    ErrorCode.REPORT_ALREADY_EXISTS: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Da co bao cao nhu vay roi",
    },
    ErrorCode.REGISTRATION_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Chua dang ky su tham gia su kien",
    },
    ErrorCode.ALREADY_REGISTERED: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Da dang ky su tham gia su kien roi",
    },
    ErrorCode.INVALID_REGISTRATION_TIME: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Thoi gian dang ky khong hop le",
    },
    ErrorCode.INVALID_EVENT_TIME: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Thoi gian su kien khong hop le",
    },
    ErrorCode.EVENT_MUST_START_AFTER_REGISTRATION: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Thoi gian su kien phai sau thoi gian dang ky",
    },
    ErrorCode.INVALID_POINT_VALUE: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Gia tri diem khong hop le",
    },
    ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Loai su kien khong hop le",
    },
    ErrorCode.SEMESTER_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Semester khong ton tai",
    },
    ErrorCode.ACTIVE_SEMESTER_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Khong co semester dang hoat dong",
    },
    ErrorCode.INVALID_SEMESTER_TIME: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Thoi gian semester khong hop le",
    },
    ErrorCode.INVALID_ID_FORMAT: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "ID không đúng định dạng ObjectId",
    },

    ErrorCode.UNIT_EVENT_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Sự kiện đẩy xuống đơn vị không tồn tại",
    },
    ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_EXISTS: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Đơn vị của bạn đã phản hồi sự kiện này rồi",
    },
    ErrorCode.UNIT_EVENT_SUBMISSION_NOT_FOUND: {
        "status": status.HTTP_404_NOT_FOUND,
        "message": "Đơn vị của bạn chưa phản hồi sự kiện này",
    },
    ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_APPROVED: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Phản hồi đã được duyệt, bạn chỉ có thể sửa khi ở trạng thái PENDING hoặc REJECTED",
    },
    ErrorCode.LIST_USER_ID_IS_REQUIRED: {
        "status": status.HTTP_400_BAD_REQUEST,
        "message": "Danh sách thành viên không được để trống",
    },
    ErrorCode.UNIT_NOT_ASSIGNED_TO_EVENT: {
        "status": status.HTTP_403_FORBIDDEN,
        "message": "Đơn vị của bạn không được giao sự kiện này",
    },
}


def app_exception(code: ErrorCode, extra_detail: Optional[str] = None) -> None:
    info = ERROR_DEFINITIONS[code]
    base_msg = info["message"]
    detail = f"{base_msg}: {extra_detail}" if extra_detail else base_msg
    raise HTTPException(status_code=info["status"], detail=detail)  # type: ignore[arg-type]

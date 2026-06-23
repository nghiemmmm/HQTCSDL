"""Framework-independent exceptions raised by application services."""

from typing import Any


class ServiceError(Exception):
    """Base class for service-layer failures."""

    default_message = "Đã xảy ra lỗi khi xử lý yêu cầu."

    def __init__(self, detail: Any = None) -> None:
        """Create an error whose public detail always contains a description."""
        if isinstance(detail, dict):
            normalized_detail = dict(detail)
            message = normalized_detail.get("message")
            if not isinstance(message, str) or not message.strip():
                normalized_detail["message"] = self.default_message
        elif isinstance(detail, str) and detail.strip():
            normalized_detail = {"message": detail.strip()}
        elif detail is None:
            normalized_detail = {"message": self.default_message}
        else:
            normalized_detail = {"message": str(detail)}

        super().__init__(normalized_detail["message"])
        self.detail: dict[str, Any] = normalized_detail


class ValidationError(ServiceError):
    """Input is syntactically valid but violates an application rule."""

    default_message = "Dữ liệu yêu cầu không hợp lệ."


class AuthenticationError(ServiceError):
    """Credentials are invalid."""

    default_message = "Thông tin đăng nhập không chính xác."


class PermissionDeniedError(ServiceError):
    """The current actor is not allowed to access a resource."""

    default_message = "Bạn không có quyền thực hiện thao tác này."


class ResourceNotFoundError(ServiceError):
    """A requested resource does not exist."""

    default_message = "Không tìm thấy dữ liệu được yêu cầu."


class ConflictError(ServiceError):
    """The operation conflicts with existing data or state."""

    default_message = "Dữ liệu hoặc trạng thái hiện tại không cho phép thao tác này."


class RepositoryError(ServiceError):
    """Persistence failed unexpectedly."""

    default_message = "Không thể xử lý dữ liệu trong cơ sở dữ liệu."

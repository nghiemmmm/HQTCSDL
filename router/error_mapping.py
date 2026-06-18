"""Translate framework-independent service errors into HTTP errors."""

from typing import NoReturn

from fastapi import HTTPException, status

from services.exceptions import (
    AuthenticationError,
    ConflictError,
    PermissionDeniedError,
    RepositoryError,
    ResourceNotFoundError,
    ServiceError,
    ValidationError,
)


def raise_http_error(error: ServiceError) -> NoReturn:
    """Raise an HTTP error with a consistently descriptive response body."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(error, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(error, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(error, PermissionDeniedError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(error, ResourceNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, ConflictError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(error, RepositoryError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = dict(error.detail)
    detail.setdefault("error_type", error.__class__.__name__)
    raise HTTPException(status_code=status_code, detail=detail) from error

"""HTTP dependencies for authentication, authorization, and database access."""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from core.session import get_session
from db.database import SessionLocal
from db.roles import Permission, has_permission

UserData = dict[str, Any]


def get_db(request: Request):
    """Yield the application database session for the current request."""
    del request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DatabaseDep = Annotated[Session, Depends(get_db)]


def get_current_user(request: Request) -> UserData:
    """Return the authenticated session user or an HTTP 401 response."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "field": "authentication",
                "message": "Bạn chưa đăng nhập vào hệ thống.",
            },
        )

    user = get_session(session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "field": "authentication",
                "message": "Phiên đăng nhập đã hết hạn hoặc không hợp lệ.",
            },
        )
    return user


CurrentUserDep = Annotated[UserData, Depends(get_current_user)]


def require_permission(permission: Permission):
    """Build an HTTP dependency requiring one permission."""

    def checker(user: CurrentUserDep) -> UserData:
        if not has_permission(user.get("role", ""), permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "field": "permission",
                    "message": "Bạn không có quyền thực hiện chức năng này.",
                },
            )
        return user

    return checker


def require_any_permission(*permissions: Permission):
    """Build an HTTP dependency requiring at least one permission."""

    def checker(user: CurrentUserDep) -> UserData:
        if not any(
            has_permission(user.get("role", ""), permission)
            for permission in permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "field": "permission",
                    "message": "Bạn không có quyền truy cập chức năng này.",
                },
            )
        return user

    return checker

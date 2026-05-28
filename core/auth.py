from fastapi import Depends, HTTPException, Request, status

from core.session import get_session
from db.roles import Permission, has_permission


def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chua dang nhap",
        )

    user = get_session(session_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phien dang nhap het han hoac khong hop le",
        )

    return user


def require_permission(permission: Permission):
    def checker(user=Depends(get_current_user)):
        if not has_permission(user.get("role"), permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong co quyen thuc hien chuc nang nay",
            )
        return user

    return checker


def require_any_permission(*permissions: Permission):
    def checker(user=Depends(get_current_user)):
        if not any(has_permission(user.get("role"), permission) for permission in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong co quyen truy cap chuc nang nay",
            )
        return user

    return checker

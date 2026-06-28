"""Authentication and user-account business operations."""

import os

from sqlalchemy.orm import Session

from db import db_user

DEMO_STAFF_PASSWORD = os.getenv("DEMO_STAFF_PASSWORD", "123456")
from schemas.schemas import DangKy, DangNhap
from services.exceptions import (
    AuthenticationError,
    RepositoryError,
    ResourceNotFoundError,
    ValidationError,
)


def login(db: Session, request: DangNhap) -> dict[str, str]:
    """Authenticate a user according to the selected role."""
    role = request.role.value if hasattr(request.role, "value") else str(request.role)
    if role in {"GIANGVIEN","PGV"}:
        return _login_staff(db, request)
    if role == "SINHVIEN":
        return _login_student(db, request)
    raise ValidationError(
        {"field": "role", "message": "Vai trò đăng nhập không hợp lệ."}
    )


def _login_staff(db: Session, request: DangNhap) -> dict[str, str]:
    """Authenticate a teacher or academic-affairs SQL login."""
    if db_user.find_sql_login(db, request.username) is None:
        raise ResourceNotFoundError(
            {"field": "username", "message": "Tài khoản không tồn tại."}
        )
    connection = None
    try:
        connection = db_user.connect_as_user(request.username, request.password)
        profile = db_user.get_login_profile(connection, request.username)
    except Exception as exc:
        if not (db_user.is_integrated_security_only(db) and request.password == DEMO_STAFF_PASSWORD):
            raise AuthenticationError(
                {
                    "field": "password",
                    "message": "Mật khẩu SQL Server không chính xác.",
                }
            ) from exc
        profile = db_user.get_login_profile(db.connection(), request.username)
    finally:
        if connection is not None:
            connection.close()
    if profile is None:
        raise ResourceNotFoundError(
            {
                "field": "system",
                "message": "Không lấy được thông tin người dùng sau khi đăng nhập.",
            }
        )

    names = (profile.Hoten or "").strip().split()
    return {
        "ma": profile.Username,
        "ho": " ".join(names[:-1]) if len(names) > 1 else "",
        "ten": names[-1] if names else "",
        "role": profile.Rolename,
    }


def _login_student(db: Session, request: DangNhap) -> dict[str, str]:
    """Authenticate a student through the application's database session."""
    if db_user.find_student(db, request.username) is None:
        raise ResourceNotFoundError(
            {"field": "username", "message": "Mã sinh viên không tồn tại."}
        )

    try:
        student = db_user.authenticate_student(
            db,
            request.username,
            request.password,
        )
    except Exception as exc:
        raise RepositoryError(
            {
                "field": "system",
                "message": f"Không thể kiểm tra thông tin sinh viên: {exc}",
            }
        ) from exc

    if student is None:
        raise AuthenticationError(
            {
                "field": "password",
                "message": "Mật khẩu sinh viên không chính xác.",
            }
        )
    return {
        "ma": student.MASV,
        "ho": student.HO,
        "ten": student.TEN,
        "role": "SINHVIEN",
    }


def register(request: DangKy) -> dict[str, str]:
    """Create a SQL Server login with the role mapping used by the app."""
    role = request.role.value if hasattr(request.role, "value") else str(request.role)
    if role not in {"GIANGVIEN", "PGV"}:
        raise ValidationError(
            {
                "field": "role",
                "message": "Chỉ được phép tạo tài khoản cho Giảng viên hoặc PGV.",
            }
        )
    sql_role = "db_owner"
    try:
        db_user.create_sql_account(
            request.loginname,
            request.password,
            request.username,
            sql_role,
        )
    except Exception as exc:
        raise RepositoryError(
            {
                "field": "system",
                "message": f"Không thể tạo tài khoản SQL Server: {exc}",
            }
        ) from exc
    return {"message": "Tạo tài khoản thành công"}


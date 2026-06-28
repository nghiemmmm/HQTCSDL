"""Authentication and user-account business operations."""

from sqlalchemy.orm import Session

from db import db_user
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
    try:
        connection = db_user.connect_as_user(request.username, request.password)
    except Exception as exc:
        raise AuthenticationError(
            {
                "field": "password",
                "message": "Mật khẩu SQL Server không chính xác.",
            }
        ) from exc

    try:
        profile = db_user.get_login_profile(connection, request.username)
    finally:
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
        "ma": (profile.Username or "").strip(),
        "ho": (" ".join(names[:-1]) if len(names) > 1 else "").strip(),
        "ten": (names[-1] if names else "").strip(),
        "role": (profile.Rolename or "").strip(),
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
        "ma": (student.MASV or "").strip(),
        "ho": (student.HO or "").strip(),
        "ten": (student.TEN or "").strip(),
        "role": "SINHVIEN",
    }


def delete_login_account(db: Session, login_name: str, current_user: dict) -> dict[str, str]:
    """Delete a SQL Server login account."""
    login_name = (login_name or "").strip()
    if not login_name:
        raise ValidationError(
            {"field": "loginname", "message": "Login name khong duoc de trong."}
        )

    current_login = (current_user.get("ma") or "").strip()
    if login_name.lower() == current_login.lower():
        raise ValidationError(
            {
                "field": "loginname",
                "message": "Khong duoc xoa tai khoan dang dang nhap.",
            }
        )

    if db_user.find_sql_login(db, login_name) is None:
        raise ResourceNotFoundError(
            {"field": "loginname", "message": "Tai khoan login khong ton tai."}
        )

    try:
        db_user.delete_sql_account(login_name)
    except Exception as exc:
        raise RepositoryError(
            {
                "field": "system",
                "message": f"Khong the xoa tai khoan login: {exc}",
            }
        ) from exc
    return {"message": f"Da xoa tai khoan login {login_name}"}


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
    sql_role = role
    try:
        db_user.create_sql_account(
            request.loginname,
            request.password,
            request.username,
            sql_role,
        )
    except Exception as exc:
        err_str = str(exc)
        # SQL Server raises error 50000 "Login name bị trùng" when loginname exists
        if "trùng" in err_str or "50000" in err_str or "duplicate" in err_str.lower():
            from services.exceptions import ConflictError
            raise ConflictError(
                {
                    "field": "loginname",
                    "message": f"Tài khoản '{request.loginname}' đã tồn tại. Vui lòng chọn tên đăng nhập khác.",
                }
            ) from exc
        raise RepositoryError(
            {
                "field": "system",
                "message": f"Không thể tạo tài khoản SQL Server: {exc}",
            }
        ) from exc
    return {"message": "Tạo tài khoản thành công"}

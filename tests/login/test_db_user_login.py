"""
Login Business Logic Tests Module

Validates login behavior while mocking database and SQL Server access.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from db import db_user
from db.roles import quyen
from schemas.schemas import DangNhap
from services import user_service
from services.exceptions import (
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
)


def test_student_login_returns_user_data_when_credentials_match(
    monkeypatch: MonkeyPatch,
) -> None:
    """Student login should return user data when credentials match."""
    db = Mock()
    del monkeypatch
    db.execute.side_effect = [
        SimpleNamespace(fetchone=lambda: SimpleNamespace(MASV="SV001")),
        SimpleNamespace(
            fetchone=lambda: SimpleNamespace(
                MASV="SV001",
                HO="Nguyen",
                TEN="An",
            )
        ),
    ]
    request = DangNhap(username="SV001", password="123456", role=quyen.SINH_VIEN)

    user_data = user_service.login(db, request)

    assert user_data == {
        "ma": "SV001",
        "ho": "Nguyen",
        "ten": "An",
        "role": "SINHVIEN",
    }


def test_student_login_raises_404_when_student_does_not_exist() -> None:
    """Student login should raise not found when student code is missing."""
    db = Mock()
    db.execute.return_value.fetchone.return_value = None
    request = DangNhap(username="SV404", password="123456", role=quyen.SINH_VIEN)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        user_service.login(db, request)

    assert exc_info.value.detail["field"] == "username"


def test_student_login_raises_401_when_password_is_wrong(
    monkeypatch: MonkeyPatch,
) -> None:
    """Student login should raise unauthorized when password is wrong."""
    db = Mock()
    del monkeypatch
    db.execute.side_effect = [
        SimpleNamespace(fetchone=lambda: SimpleNamespace(MASV="SV001")),
        SimpleNamespace(fetchone=lambda: None),
    ]
    request = DangNhap(username="SV001", password="wrong", role=quyen.SINH_VIEN)

    with pytest.raises(AuthenticationError) as exc_info:
        user_service.login(db, request)

    assert exc_info.value.detail["field"] == "password"


def test_teacher_login_returns_user_data_when_sql_login_succeeds(
    monkeypatch: MonkeyPatch,
) -> None:
    """Teacher login should return user data when SQL login succeeds."""
    db = Mock()
    db.execute.return_value.fetchone.return_value = SimpleNamespace(login_name="GV001")
    sql_connection = Mock()
    sql_connection.execute.return_value.fetchone.return_value = SimpleNamespace(
        Username="GV001",
        Hoten="Nguyen Van Binh",
        Rolename="GIANGVIEN",
    )
    sql_engine = Mock()
    sql_engine.connect.return_value = sql_connection
    monkeypatch.setattr(db_user, "create_engine", lambda connection_url: sql_engine)
    request = DangNhap(username="GV001", password="secret", role=quyen.GIANG_VIEN)

    user_data = user_service.login(db, request)

    assert user_data == {
        "ma": "GV001",
        "ho": "Nguyen Van",
        "ten": "Binh",
        "role": "GIANGVIEN",
    }
    sql_connection.close.assert_called_once()


def test_teacher_login_raises_404_when_sql_login_does_not_exist() -> None:
    """Teacher login should raise not found when SQL login is missing."""
    db = Mock()
    db.execute.return_value.fetchone.return_value = None
    request = DangNhap(username="missing", password="secret", role=quyen.GIANG_VIEN)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        user_service.login(db, request)

    assert exc_info.value.detail["field"] == "username"


def test_teacher_login_raises_401_when_sql_password_is_wrong(
    monkeypatch: MonkeyPatch,
) -> None:
    """Teacher login should raise unauthorized when SQL password is wrong."""
    db = Mock()
    db.execute.return_value.fetchone.return_value = SimpleNamespace(login_name="GV001")

    def raise_connection_error(connection_url):
        raise RuntimeError("login failed")

    monkeypatch.setattr(db_user, "create_engine", raise_connection_error)
    request = DangNhap(username="GV001", password="wrong", role=quyen.GIANG_VIEN)

    with pytest.raises(AuthenticationError) as exc_info:
        user_service.login(db, request)

    assert exc_info.value.detail["field"] == "password"


def test_teacher_login_raises_404_when_profile_sp_returns_no_data(
    monkeypatch: MonkeyPatch,
) -> None:
    """Teacher login should raise not found when profile SP has no data."""
    db = Mock()
    db.execute.return_value.fetchone.return_value = SimpleNamespace(login_name="GV001")
    sql_connection = Mock()
    sql_connection.execute.return_value.fetchone.return_value = None
    sql_engine = Mock()
    sql_engine.connect.return_value = sql_connection
    monkeypatch.setattr(db_user, "create_engine", lambda connection_url: sql_engine)
    request = DangNhap(username="GV001", password="secret", role=quyen.GIANG_VIEN)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        user_service.login(db, request)

    assert exc_info.value.detail["field"] == "system"


def test_login_raises_400_when_role_is_invalid() -> None:
    """Login should raise bad request when role is invalid."""
    db = Mock()
    request = SimpleNamespace(username="user", password="secret", role="OTHER")

    with pytest.raises(ValidationError) as exc_info:
        user_service.login(db, request)

    assert exc_info.value.detail["field"] == "role"

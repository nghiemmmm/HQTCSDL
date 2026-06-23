from datetime import datetime
from unittest.mock import Mock

import pytest

from db import db_dangkythi
from db.model import DbGiaoVienDangKy
from db.roles import Permission, has_permission
from schemas.schemas import DangKyThi
from services import exam_registration_service


def _registration_request(magv: str = "FORGED") -> DangKyThi:
    return DangKyThi(
        magv=magv,
        mamh="MH001",
        malop="D21CQCN01",
        trinhdo="A",
        ngaythi=datetime(2026, 7, 1, 8, 0),
        lan=1,
        socauthi=40,
        thoigian=45,
    )


@pytest.mark.parametrize("role", ["GIANGVIEN", "PGV"])
def test_create_registration_uses_logged_in_magv(
    monkeypatch: pytest.MonkeyPatch,
    role: str,
) -> None:
    db = Mock()
    request = _registration_request()
    created = DbGiaoVienDangKy(
        magv="GV001",
        mamh=request.mamh,
        malop=request.malop,
        lan=request.lan,
    )

    monkeypatch.setattr(db_dangkythi, "get_subject", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_class", lambda *_: object())
    monkeypatch.setattr(
        db_dangkythi,
        "get_teacher",
        lambda _db, magv: object() if magv == "GV001" else None,
    )
    monkeypatch.setattr(db_dangkythi, "get_registration", lambda *_: None)
    monkeypatch.setattr(
        db_dangkythi,
        "check_question_count_with_procedure",
        lambda *_: (1, 40, "Đủ câu hỏi"),
    )
    monkeypatch.setattr(db_dangkythi, "create", lambda _db, _request: created)

    result = exam_registration_service.create_registration(
        db,
        request,
        {"ma": " GV001 ", "role": role},
    )

    assert request.magv == "GV001"
    assert request.magv != "FORGED"
    assert result is created


def test_pgv_has_exam_registration_management_permissions() -> None:
    assert has_permission("PGV", Permission.CREATE_EXAM_REGISTRATION)
    assert has_permission("PGV", Permission.UPDATE_EXAM_REGISTRATION)
    assert has_permission("PGV", Permission.DELETE_EXAM_REGISTRATION)

from datetime import datetime
from unittest.mock import Mock

import pytest

from db import db_dangkythi
from db.model import DbGiaoVienDangKy
from db.roles import Permission, has_permission
from schemas.schemas import DangKyThi
from services import exam_registration_service
from services.exceptions import ConflictError, PermissionDeniedError, ValidationError


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


def _existing_registration(magv: str = "GV001") -> DbGiaoVienDangKy:
    return DbGiaoVienDangKy(
        magv=magv,
        mamh="MH001",
        malop="D21CQCN01",
        trinhdo="A",
        lan=1,
        socauthi=40,
        thoigian=45,
        ngaythi=datetime(2026, 7, 1, 8, 0),
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


def test_update_registration_blocks_other_teacher(monkeypatch: pytest.MonkeyPatch) -> None:
    db = Mock()
    request = _registration_request(magv="GV001")

    monkeypatch.setattr(
        db_dangkythi,
        "get_registration_entity",
        lambda *_: _existing_registration(magv="GV002"),
    )

    with pytest.raises(PermissionDeniedError):
        exam_registration_service.update_registration(
            db,
            "D21CQCN01",
            "MH001",
            1,
            request,
            {"ma": "GV001", "role": "GIANGVIEN"},
        )


def test_update_registration_blocks_when_exam_date_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    db = Mock()
    request = _registration_request(magv="GV001")
    past_registration = _existing_registration()
    past_registration.ngaythi = datetime(2020, 1, 1, 8, 0) # Past date

    monkeypatch.setattr(
        db_dangkythi,
        "get_registration_entity",
        lambda *_: past_registration,
    )

    with pytest.raises(ConflictError) as exc_info:
        exam_registration_service.update_registration(
            db,
            "D21CQCN01",
            "MH001",
            1,
            request,
            {"ma": "GV001", "role": "GIANGVIEN"},
        )
    assert "Chỉ được sửa hoặc xóa lịch thi chưa đến ngày thi" in str(exc_info.value)


def test_delete_registration_blocks_when_exam_date_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    db = Mock()
    past_registration = _existing_registration()
    past_registration.ngaythi = datetime(2020, 1, 1, 8, 0) # Past date

    monkeypatch.setattr(
        db_dangkythi,
        "get_registration_entity",
        lambda *_: past_registration,
    )

    with pytest.raises(ConflictError) as exc_info:
        exam_registration_service.delete_registration(
            db,
            "D21CQCN01",
            "MH001",
            1,
            {"ma": "GV001", "role": "GIANGVIEN"},
        )
    assert "Chỉ được sửa hoặc xóa lịch thi chưa đến ngày thi" in str(exc_info.value)


def test_update_registration_rechecks_questions_when_setup_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = Mock()
    request = _registration_request(magv="IGNORED")
    request.trinhdo = "B"
    request.socauthi = 50
    existing = _existing_registration()
    updated = _existing_registration()
    called = Mock(return_value={"is_hop_le": True, "thong_bao": "OK"})

    monkeypatch.setattr(db_dangkythi, "get_registration_entity", lambda *_: existing)
    monkeypatch.setattr(db_dangkythi, "has_exam_result", lambda *_: False)
    monkeypatch.setattr(db_dangkythi, "has_exam_session", lambda *_: False)
    monkeypatch.setattr(db_dangkythi, "get_subject", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_class", lambda *_: object())
    monkeypatch.setattr(exam_registration_service, "check_question_availability", called)
    monkeypatch.setattr(db_dangkythi, "update", lambda _db, _entity, _request: updated)

    result = exam_registration_service.update_registration(
        db,
        "D21CQCN01",
        "MH001",
        1,
        request,
        {"ma": "GV001", "role": "GIANGVIEN"},
    )

    assert result is updated
    assert request.magv == "GV001"
    called.assert_called_once_with(db, "MH001", "B", 50)


def test_create_registration_attempt_2_date_must_be_after_attempt_1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = Mock()
    attempt_1 = DbGiaoVienDangKy(
        magv="GV001",
        mamh="MH001",
        malop="D21CQCN01",
        trinhdo="A",
        lan=1,
        socauthi=40,
        thoigian=45,
        ngaythi=datetime(2026, 7, 25, 8, 0),
    )
    
    request = _registration_request()
    request.lan = 2
    request.ngaythi = datetime(2026, 7, 25, 14, 0)
    request.magv = "GV001"

    monkeypatch.setattr(db_dangkythi, "get_subject", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_class", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_teacher", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_registration", lambda _db, malop, mamh, lan: attempt_1 if lan == 1 else None)

    with pytest.raises(ValidationError) as exc_info:
        exam_registration_service.create_registration(
            db,
            request,
            {"ma": "GV001", "role": "GIANGVIEN"},
        )
    assert "Ngay thi lan 2 phai sau ngay thi lan 1 it nhat 1 ngay" in str(exc_info.value)


def test_create_registration_attempt_2_date_accepted_if_next_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = Mock()
    attempt_1 = DbGiaoVienDangKy(
        magv="GV001",
        mamh="MH001",
        malop="D21CQCN01",
        trinhdo="A",
        lan=1,
        socauthi=40,
        thoigian=45,
        ngaythi=datetime(2026, 7, 25, 8, 0),
    )
    
    request = _registration_request()
    request.lan = 2
    request.ngaythi = datetime(2026, 7, 26, 8, 0)
    request.magv = "GV001"

    monkeypatch.setattr(db_dangkythi, "get_subject", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_class", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_teacher", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_registration", lambda _db, malop, mamh, lan: attempt_1 if lan == 1 else None)
    monkeypatch.setattr(db_dangkythi, "check_question_count_with_procedure", lambda *_: (1, 40, "Đủ câu hỏi"))
    monkeypatch.setattr(db_dangkythi, "create", lambda _db, _request: DbGiaoVienDangKy())

    exam_registration_service.create_registration(
        db,
        request,
        {"ma": "GV001", "role": "GIANGVIEN"},
    )


def test_create_registration_fails_when_questions_insufficient(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = Mock()
    request = _registration_request()
    request.socauthi = 50

    monkeypatch.setattr(db_dangkythi, "get_subject", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_class", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_teacher", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_registration", lambda *_: None)
    monkeypatch.setattr(
        db_dangkythi,
        "check_question_count_with_procedure",
        lambda *_: (0, 30, "Không đủ câu hỏi"),
    )

    with pytest.raises(ConflictError) as exc_info:
        exam_registration_service.create_registration(
            db,
            request,
            {"ma": "GV001", "role": "GIANGVIEN"},
        )
    assert "Không đủ câu hỏi cho môn MH001, trình độ A" in str(exc_info.value)
    assert "Yêu cầu 50 câu, hiện có 30 câu" in str(exc_info.value)


def test_create_registration_fails_when_exam_date_is_today(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = Mock()
    request = _registration_request()
    request.ngaythi = datetime.now() # Today (invalid, must be tomorrow or later)

    monkeypatch.setattr(db_dangkythi, "get_subject", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_class", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_teacher", lambda *_: object())
    monkeypatch.setattr(db_dangkythi, "get_registration", lambda *_: None)

    with pytest.raises(ValidationError) as exc_info:
        exam_registration_service.create_registration(
            db,
            request,
            {"ma": "GV001", "role": "GIANGVIEN"},
        )
    assert "Ngày thi đăng ký phải bắt đầu từ ngày mai trở đi" in str(exc_info.value)




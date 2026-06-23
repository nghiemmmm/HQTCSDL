"""Business operations for exam registrations."""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_dangkythi
from db.model import DbGiaoVienDangKy, DbLop, DbMonHoc
from schemas.schemas import DangKyThi
from services.exceptions import (
    ConflictError,
    PermissionDeniedError,
    RepositoryError,
    ResourceNotFoundError,
    ValidationError,
)

MIN_REGISTRATION_LEAD_TIME_MINUTES = 30


def create_registration(
    db: Session,
    request: DangKyThi,
    user: dict[str, Any],
) -> DbGiaoVienDangKy:
    """Validate and create an exam registration."""
    if db_dangkythi.get_subject(db, request.mamh) is None:
        raise ResourceNotFoundError(f"Mon hoc voi ma {request.mamh} khong ton tai")
    if db_dangkythi.get_class(db, request.malop) is None:
        raise ResourceNotFoundError(f"Lop voi ma {request.malop} khong ton tai")

    if request.ngaythi:
        min_allowed_time = datetime.now() + timedelta(
            minutes=MIN_REGISTRATION_LEAD_TIME_MINUTES
        )
        if request.ngaythi < min_allowed_time:
            raise ValidationError(
                f"Ngay thi phai lon hon thoi gian hien tai it nhat "
                f"{MIN_REGISTRATION_LEAD_TIME_MINUTES} phut."
            )

    if user.get("role") in {"GIANGVIEN", "PGV"}:
        request.magv = (user.get("ma") or "").strip()
    if not request.magv:
        raise ValidationError(
            "Khong xac dinh duoc MAGV tu tai khoan dang dang nhap"
        )
    if db_dangkythi.get_teacher(db, request.magv) is None:
        raise ResourceNotFoundError(
            f"Giao vien voi ma {request.magv} khong ton tai"
        )
    if db_dangkythi.get_registration(
        db,
        request.malop,
        request.mamh,
        request.lan,
    ):
        raise ConflictError(
            f"Lich thi cho lop {request.malop}, mon {request.mamh} "
            f"lan {request.lan} da duoc dang ky."
        )

    _validate_question_count(db, request)
    try:
        return db_dangkythi.create(db, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc


def update_registration(
    db: Session,
    malop: str,
    mamh: str,
    lan: int,
    request: DangKyThi,
    user: dict[str, Any],
) -> DbGiaoVienDangKy:
    """Update an exam registration when no exam data exists yet."""
    registration = _get_registration_or_raise(db, malop, mamh, lan)
    _ensure_registration_owner(registration, user)
    _ensure_registration_not_used(db, malop, mamh, lan)

    if db_dangkythi.get_subject(db, request.mamh) is None:
        raise ResourceNotFoundError(f"Mon hoc voi ma {request.mamh} khong ton tai")
    if db_dangkythi.get_class(db, request.malop) is None:
        raise ResourceNotFoundError(f"Lop voi ma {request.malop} khong ton tai")
    if request.malop != malop or request.mamh != mamh or request.lan != lan:
        raise ValidationError("Khong duoc thay doi lop, mon hoc hoac lan thi khi sua lich")

    if request.ngaythi:
        min_allowed_time = datetime.now() + timedelta(
            minutes=MIN_REGISTRATION_LEAD_TIME_MINUTES
        )
        if request.ngaythi < min_allowed_time:
            raise ValidationError(
                f"Ngay thi phai lon hon thoi gian hien tai it nhat "
                f"{MIN_REGISTRATION_LEAD_TIME_MINUTES} phut."
            )

    question_setup_changed = (
        (registration.trinhdo or "").strip() != (request.trinhdo or "").strip()
        or registration.socauthi != request.socauthi
    )
    if question_setup_changed:
        _validate_question_count(db, request)

    request.magv = registration.magv
    try:
        return db_dangkythi.update(db, registration, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc


def delete_registration(
    db: Session,
    malop: str,
    mamh: str,
    lan: int,
    user: dict[str, Any],
) -> dict[str, str]:
    """Delete an unused exam registration."""
    registration = _get_registration_or_raise(db, malop, mamh, lan)
    _ensure_registration_owner(registration, user)
    _ensure_registration_not_used(db, malop, mamh, lan)

    try:
        db_dangkythi.delete(db, registration)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {"message": "Da xoa lich thi thanh cong"}


def _get_registration_or_raise(
    db: Session,
    malop: str,
    mamh: str,
    lan: int,
) -> DbGiaoVienDangKy:
    registration = db_dangkythi.get_registration_entity(db, malop, mamh, lan)
    if registration is None:
        raise ResourceNotFoundError(
            f"Khong tim thay lich thi lop {malop}, mon {mamh}, lan {lan}"
        )
    return registration


def _ensure_registration_owner(
    registration: DbGiaoVienDangKy,
    user: dict[str, Any],
) -> None:
    if user.get("role") != "GIANGVIEN":
        return
    teacher_id = (user.get("ma") or "").strip()
    registration_teacher = (registration.magv or "").strip()
    if registration_teacher != teacher_id:
        raise PermissionDeniedError("Khong duoc sua/xoa lich thi cua giao vien khac")


def _ensure_registration_not_used(
    db: Session,
    malop: str,
    mamh: str,
    lan: int,
) -> None:
    if db_dangkythi.has_exam_result(db, malop, mamh, lan):
        raise ConflictError("Khong the sua/xoa lich thi da co sinh vien thi")
    if db_dangkythi.has_exam_session(db, malop, mamh, lan):
        raise ConflictError("Khong the sua/xoa lich thi da co phien thi")


def _validate_question_count(db: Session, request: DangKyThi) -> None:
    """Validate question availability before saving a registration."""
    result = check_question_availability(
        db,
        request.mamh,
        request.trinhdo or "",
        request.socauthi or 0,
    )
    if not result["is_hop_le"]:
        raise ConflictError(result["thong_bao"])


def check_question_availability(
    db: Session,
    mamh: str,
    trinhdo: str,
    socauthi: int,
) -> dict:
    """Check if the question bank has enough questions for an exam setup."""
    try:
        row = db_dangkythi.check_question_count_with_procedure(
            db,
            mamh,
            trinhdo,
            socauthi,
        )
        if row:
            return {
                "is_hop_le": bool(row[0]),
                "so_cau_co_san": row[1],
                "so_cau_yeu_cau": socauthi,
                "thong_bao": row[2],
            }
    except Exception:
        count = db_dangkythi.count_questions(db, mamh, trinhdo)
        return _question_count_result(count, socauthi)

    count = db_dangkythi.count_questions(db, mamh, trinhdo)
    return _question_count_result(count, socauthi)


def _question_count_result(count: int, required: int) -> dict:
    is_valid = count >= required
    return {
        "is_hop_le": is_valid,
        "so_cau_co_san": count,
        "so_cau_yeu_cau": required,
        "thong_bao": (
            "Du cau hoi thi"
            if is_valid
            else f"Khong du cau hoi. Yeu cau: {required}, Hien co: {count}"
        ),
    }


def list_registered_subjects(db: Session, teacher_id: str) -> list[DbMonHoc]:
    """Return subjects registered by a teacher."""
    try:
        return db_dangkythi.get_monhocdk(db, teacher_id)
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Loi khi lay mon hoc dang ky: {exc}") from exc


def list_classes(db: Session) -> list[DbLop]:
    """Return classes available for exam registration."""
    try:
        return db_dangkythi.get_all_classes(db)
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Khong the lay danh sach lop: {exc}") from exc


def list_subjects(db: Session) -> list[DbMonHoc]:
    """Return subjects available for exam registration."""
    try:
        return db_dangkythi.get_all_subjects(db)
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Khong the lay danh sach mon hoc: {exc}") from exc


def list_registrations(
    db: Session,
    user: dict[str, Any],
    keyword: str | None = None,
) -> list[dict]:
    """Return exam registrations for the registration-management page."""
    is_teacher = user.get("role") == "GIANGVIEN"
    teacher_id = (user.get("ma") or "").strip()
    try:
        if is_teacher and keyword and keyword.strip():
            rows = db_dangkythi.search_registrations_by_teacher(
                db,
                teacher_id,
                keyword,
            )
        elif is_teacher:
            rows = db_dangkythi.get_by_teacher(db, teacher_id)
        elif keyword and keyword.strip():
            rows = db_dangkythi.search_registrations(db, keyword)
        else:
            rows = db_dangkythi.get_all(db)
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Khong the lay danh sach lich thi: {exc}") from exc

    return [_registration_to_dict(row) for row in rows]


def _registration_to_dict(row: DbGiaoVienDangKy) -> dict:
    exam_date = row.ngaythi
    return {
        "malop": (row.malop or "").strip(),
        "mamh": (row.mamh or "").strip(),
        "lan": row.lan,
        "magv": (row.magv or "").strip(),
        "trinhdo": (row.trinhdo or "").strip(),
        "ngaythi": exam_date.isoformat() if exam_date else "",
        "ngaythi_text": exam_date.strftime("%d/%m/%Y %H:%M") if exam_date else "",
        "socauthi": row.socauthi,
        "thoigian": row.thoigian,
    }


def list_registrations_in_range(db: Session, from_date: str, to_date: str) -> list[dict]:
    """Validate date range and retrieve exam registrations."""
    try:
        rows = db_dangkythi.list_registrations_in_range(db, from_date, to_date)
        results = []
        for row in rows:
            results.append({
                "tenlop": (row[0] or "").strip(),
                "tenmh": (row[1] or "").strip(),
                "hoten": (row[2] or "").strip(),
                "socauthi": row[3],
                "ngaythi": row[4].strftime("%d/%m/%Y") if row[4] else "",
                "dathi": (row[5] or "").strip(),
            })
        return results
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Loi khi lay danh sach dang ky thi: {exc}") from exc

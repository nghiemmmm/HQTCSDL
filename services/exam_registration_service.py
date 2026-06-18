"""Business operations for exam registrations."""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_dangkythi
from db.model import DbGiaoVienDangKy, DbMonHoc
from schemas.schemas import DangKyThi
from services.exceptions import ConflictError, RepositoryError, ResourceNotFoundError


def create_registration(
    db: Session,
    request: DangKyThi,
    user: dict[str, Any],
) -> DbGiaoVienDangKy:
    """Validate and create an exam registration."""
    if db_dangkythi.get_subject(db, request.mamh) is None:
        raise ResourceNotFoundError(f"Môn học với mã {request.mamh} không tồn tại")
    if db_dangkythi.get_class(db, request.malop) is None:
        raise ResourceNotFoundError(f"Lớp với mã {request.malop} không tồn tại")

    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma")
    if request.magv and db_dangkythi.get_teacher(db, request.magv) is None:
        raise ResourceNotFoundError(
            f"Giáo viên với mã {request.magv} không tồn tại"
        )
    if db_dangkythi.get_registration(
        db,
        request.malop,
        request.mamh,
        request.lan,
    ):
        raise ConflictError(
            f"Lịch thi cho lớp {request.malop}, môn {request.mamh} "
            f"lần {request.lan} đã được đăng ký."
        )

    _validate_question_count(db, request)
    try:
        return db_dangkythi.create(db, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc


def _validate_question_count(db: Session, request: DangKyThi) -> None:
    """Validate question availability using the procedure with ORM fallback."""
    try:
        row = db_dangkythi.check_question_count_with_procedure(
            db,
            request.mamh,
            request.trinhdo or "",
            request.socauthi or 0,
        )
        if row and row[0] == 0:
            raise ConflictError(row[2])
        return
    except ConflictError:
        raise
    except Exception:
        count = db_dangkythi.count_questions(
            db,
            request.mamh,
            request.trinhdo or "",
        )
        if count < (request.socauthi or 0):
            raise ConflictError(
                f"Không đủ câu hỏi. Yêu cầu: {request.socauthi}, Hiện có: {count}"
            )


def list_registered_subjects(db: Session, teacher_id: str) -> list[DbMonHoc]:
    """Return subjects registered by a teacher."""
    try:
        return db_dangkythi.get_monhocdk(db, teacher_id)
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Lỗi khi lấy môn học đăng ký: {exc}") from exc


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
                "dathi": (row[5] or "").strip()
            })
        return results
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Lỗi khi lấy danh sách đăng ký thi: {exc}") from exc

"""Business operations for subjects."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_monhoc
from db.model import DbMonHoc
from schemas.schemas import MonHocBase
from services.exceptions import ConflictError, RepositoryError, ResourceNotFoundError


def list_subjects(db: Session) -> list[DbMonHoc]:
    """Return all subjects."""
    try:
        return db_monhoc.get_all(db)
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Lỗi cơ sở dữ liệu khi truy xuất môn học: {exc}") from exc


def get_subject(db: Session, mamh: str) -> DbMonHoc:
    """Return a subject or raise a domain not-found error."""
    subject = db_monhoc.get_by_id(db, mamh)
    if subject is None:
        raise ResourceNotFoundError("Không tìm thấy môn học")
    return subject


def search_subjects(db: Session, keyword: str) -> list[DbMonHoc]:
    """Search subjects, returning all when the keyword is empty."""
    return db_monhoc.search(db, keyword) if keyword else list_subjects(db)


def create_subject(db: Session, request: MonHocBase) -> dict:
    """Create a subject after duplicate checks."""
    status = db_monhoc.check_subject_existence(db, request.mamh, request.tenmh)
    if status == 1:
        raise ConflictError("Mã môn học đã tồn tại")
    elif status == 2:
        raise ConflictError("Tên môn học đã tồn tại")
    try:
        subject = db_monhoc.create(db, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {
        "message": f"Thêm thành công môn học: {subject.tenmh}",
        "data": {"mamh": subject.mamh, "tenmh": subject.tenmh},
    }


def update_subject(db: Session, mamh: str, request: MonHocBase) -> dict:
    """Update a subject when it has not been used for an exam."""
    subject = get_subject(db, mamh)
    if db_monhoc.has_exam_registration(db, mamh):
        raise ConflictError("Đã đăng ký thi không được sửa")
    try:
        db_monhoc.check_subject_update_conflict(db, mamh, request.tenmh)
    except (SQLAlchemyError, ValueError) as exc:
        orig_msg = str(exc)
        import re
        match = re.search(r"\[SQL Server\]\s*(.*)", orig_msg)
        if match:
            clean_msg = match.group(1).split(' (')[0].strip()
        else:
            clean_msg = "Tên môn học đã tồn tại"
        raise ConflictError(clean_msg) from exc
    try:
        subject = db_monhoc.update(db, subject, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {
        "message": f"Sửa thành công môn học: {subject.tenmh}",
        "data": {"mamh": subject.mamh, "tenmh": subject.tenmh},
    }


def delete_subject(db: Session, mamh: str) -> dict[str, str]:
    """Delete a subject when it has not been used for an exam."""
    subject = get_subject(db, mamh)
    if db_monhoc.has_exam_registration(db, mamh):
        raise ConflictError("Đã đăng ký thi không được xóa")
    name = subject.tenmh
    try:
        db_monhoc.delete(db, subject)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {"message": f"Xóa thành công môn học: {name}"}



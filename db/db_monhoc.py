"""Subject repository containing SQLAlchemy persistence operations only."""

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from db.model import DbGiaoVienDangKy, DbMonHoc
from schemas.schemas import MonHocBase


def _clean(value: str | None) -> str:
    return (value or "").strip()


def get_all(db: Session) -> list[DbMonHoc]:
    """Return all subjects."""
    return db.query(DbMonHoc).all()


def get_by_id(db: Session, mamh: str) -> DbMonHoc | None:
    """Return one subject by code."""
    return db.query(DbMonHoc).filter(func.trim(DbMonHoc.mamh) == _clean(mamh)).first()


def get_by_name(db: Session, tenmh: str) -> DbMonHoc | None:
    """Return one subject by name."""
    return db.query(DbMonHoc).filter(func.trim(DbMonHoc.tenmh) == _clean(tenmh)).first()


def create(db: Session, request: MonHocBase) -> DbMonHoc:
    """Insert and return a subject."""
    subject = DbMonHoc(**request.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def update(db: Session, subject: DbMonHoc, request: MonHocBase) -> DbMonHoc:
    """Persist changes to an existing subject."""
    subject.tenmh = request.tenmh
    db.commit()
    db.refresh(subject)
    return subject


def delete(db: Session, subject: DbMonHoc) -> None:
    """Delete an existing subject."""
    db.delete(subject)
    db.commit()


def search(db: Session, keyword: str) -> list[DbMonHoc]:
    """Search subjects by code or name."""
    return db.query(DbMonHoc).filter(
        or_(
            DbMonHoc.mamh.ilike(f"%{keyword}%"),
            DbMonHoc.tenmh.ilike(f"%{keyword}%"),
        )
    ).all()


def has_exam_registration(db: Session, mamh: str) -> bool:
    """Return whether the subject is referenced by an exam registration."""
    return db.query(DbGiaoVienDangKy).filter(
        func.trim(DbGiaoVienDangKy.mamh) == _clean(mamh)
    ).first() is not None


def check_subject_existence(db: Session, mamh: str, tenmh: str) -> int:
    """Return 1 when code exists, 2 when name exists, otherwise 0."""
    subject_code = _clean(mamh)
    subject_name = _clean(tenmh)

    if db.query(DbMonHoc).filter(func.trim(DbMonHoc.mamh) == subject_code).first():
        return 1
    if db.query(DbMonHoc).filter(func.trim(DbMonHoc.tenmh) == subject_name).first():
        return 2
    return 0


def check_subject_update_conflict(db: Session, mamh: str, tenmh: str) -> None:
    """Raise ValueError when the new subject name is used by another subject."""
    subject_code = _clean(mamh)
    subject_name = _clean(tenmh)
    existing = db.query(DbMonHoc).filter(
        func.trim(DbMonHoc.tenmh) == subject_name,
        func.trim(DbMonHoc.mamh) != subject_code,
    ).first()
    if existing:
        raise ValueError("Ten mon hoc da ton tai")

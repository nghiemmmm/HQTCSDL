"""Subject repository containing SQLAlchemy persistence operations only."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from db.model import DbGiaoVienDangKy, DbMonHoc
from schemas.schemas import MonHocBase


def get_all(db: Session) -> list[DbMonHoc]:
    """Return all subjects."""
    return db.query(DbMonHoc).all()


def get_by_id(db: Session, mamh: str) -> DbMonHoc | None:
    """Return one subject by code."""
    return db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh).first()


def get_by_name(db: Session, tenmh: str) -> DbMonHoc | None:
    """Return one subject by name."""
    return db.query(DbMonHoc).filter(DbMonHoc.tenmh == tenmh).first()


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
        DbGiaoVienDangKy.mamh == mamh
    ).first() is not None


def check_subject_existence(db: Session, mamh: str, tenmh: str) -> int:
    """Check if subject code or name exists using SP_KT_MonHoc_Ton_Tai."""
    from sqlalchemy import text
    query = text("EXEC SP_KT_MonHoc_Ton_Tai @MAMH = :mamh, @TENMH = :tenmh")
    row = db.execute(query, {
        "mamh": mamh.strip(),
        "tenmh": tenmh.strip()
    }).fetchone()
    
    if row:
        return int(row[0])
    return 0


def check_subject_update_conflict(db: Session, mamh: str, tenmh: str) -> None:
    """Check if the new subject name conflicts with another subject using SP_KT_Sua_MonHoc_Ton_Tai."""
    from sqlalchemy import text
    query = text("EXEC SP_KT_Sua_MonHoc_Ton_Tai @MAMH = :mamh, @TENMH = :tenmh")
    db.execute(query, {
        "mamh": mamh.strip(),
        "tenmh": tenmh.strip()
    })



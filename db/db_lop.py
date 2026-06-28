"""Class repository containing persistence operations only."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from db.model import DbLop, DbSinhVien
from schemas.schemas import LopDisplay


def get_all_lop(db: Session) -> list[DbLop]:
    """Return all classes."""
    return db.query(DbLop).order_by(DbLop.malop.asc()).all()


def get_by_id(db: Session, malop: str) -> DbLop | None:
    """Return one class by code."""
    return db.query(DbLop).filter(func.trim(DbLop.malop) == malop.strip()).first()


def get_by_name(db: Session, tenlop: str) -> DbLop | None:
    """Return one class by name."""
    return db.query(DbLop).filter(func.trim(DbLop.tenlop) == tenlop.strip()).first()


def count_students(db: Session, malop: str) -> int:
    """Count students in a class."""
    return (
        db.query(DbSinhVien)
        .filter(func.trim(DbSinhVien.malop) == malop.strip())
        .count()
    )


def them_lop(db: Session, lop: LopDisplay) -> DbLop:
    """Insert a class."""
    entity = DbLop(malop=lop.malop, tenlop=lop.tenlop)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def sua_lop(db: Session, entity: DbLop, lop: LopDisplay) -> DbLop:
    """Persist class changes."""
    entity.tenlop = lop.tenlop
    db.commit()
    db.refresh(entity)
    return entity


def xoa_lop(db: Session, entity: DbLop) -> None:
    """Delete a class."""
    db.delete(entity)
    db.commit()


def check_class_existence(db: Session, malop: str, tenlop: str) -> int:
    """Check if class code or class name exists."""
    code = malop.strip()
    name = tenlop.strip()
    if code and get_by_id(db, code):
        return 1
    if name and get_by_name(db, name):
        return 2
    return 0


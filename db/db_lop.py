"""Class repository containing persistence operations only."""

from sqlalchemy.orm import Session

from db.model import DbLop, DbSinhVien
from schemas.schemas import LopDisplay


def get_all_lop(db: Session) -> list[DbLop]:
    """Return all classes."""
    return db.query(DbLop).order_by(DbLop.malop.asc()).all()


def get_by_id(db: Session, malop: str) -> DbLop | None:
    """Return one class by code."""
    return db.query(DbLop).filter(DbLop.malop == malop).first()


def get_by_name(db: Session, tenlop: str) -> DbLop | None:
    """Return one class by name."""
    return db.query(DbLop).filter(DbLop.tenlop == tenlop).first()


def count_students(db: Session, malop: str) -> int:
    """Count students in a class."""
    return db.query(DbSinhVien).filter(DbSinhVien.malop == malop).count()


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
    """Check if class code or class name exists using SP_KT_Lop_Ton_Tai."""
    from sqlalchemy import text
    query = text("EXEC SP_KT_Lop_Ton_Tai @MALOP = :malop, @TENLOP = :tenlop")
    row = db.execute(query, {
        "malop": malop.strip(),
        "tenlop": tenlop.strip()
    }).fetchone()
    
    if row:
        return int(row[0])
    return 0


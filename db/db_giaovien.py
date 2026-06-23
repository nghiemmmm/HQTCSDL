"""Teacher repository containing database operations only."""

from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from db.model import DbGiaoVien
from schemas.schemas import GiaoVienCreate, GiaoVienUpdate


def get_all_gv(db: Session) -> list[DbGiaoVien]:
    """Return all teachers."""
    return db.query(DbGiaoVien).all()


def get_ds_gv_chua_quyen(db: Session) -> list:
    """Return rows from the unregistered-teacher stored procedure."""
    return db.execute(text("EXEC SP_GET_GV_CHUA_DK")).fetchall()


def get_all(db: Session) -> list[DbGiaoVien]:
    """Return all teachers."""
    return db.query(DbGiaoVien).all()


def get_by_id(db: Session, magv: str) -> DbGiaoVien | None:
    """Return one teacher."""
    return db.query(DbGiaoVien).filter(DbGiaoVien.magv == magv).first()


def create(db: Session, request: GiaoVienCreate) -> DbGiaoVien:
    """Insert a teacher."""
    teacher = DbGiaoVien(**request.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def update(db: Session, teacher: DbGiaoVien, request: GiaoVienUpdate) -> DbGiaoVien:
    """Persist teacher changes."""
    for field, value in request.model_dump(exclude={"magv"}).items():
        setattr(teacher, field, value)
    db.commit()
    db.refresh(teacher)
    return teacher


def delete(db: Session, teacher: DbGiaoVien) -> None:
    """Delete a teacher."""
    db.delete(teacher)
    db.commit()


def search(db: Session, keyword: str) -> list[DbGiaoVien]:
    """Search teachers by code or name."""
    return db.query(DbGiaoVien).filter(
        or_(
            DbGiaoVien.magv.ilike(f"%{keyword}%"),
            DbGiaoVien.ho.ilike(f"%{keyword}%"),
            DbGiaoVien.ten.ilike(f"%{keyword}%"),
        )
    ).all()

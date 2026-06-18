"""Student repository containing persistence operations only."""

from sqlalchemy.orm import Session

from db.model import DbSinhVien
from schemas.schemas import SinhVienBase


def get_by_id(db: Session, masv: str) -> DbSinhVien | None:
    """Return one student."""
    return db.query(DbSinhVien).filter(DbSinhVien.masv == masv).first()


def lay_ds_sinh_vien_mot_lop(db: Session, malop: str) -> list[DbSinhVien]:
    """Return students assigned to a class."""
    return (
        db.query(DbSinhVien)
        .filter(DbSinhVien.malop == malop)
        .order_by(DbSinhVien.masv.asc())
        .all()
    )


def sl_sinhvien_mot_lop(db: Session, malop: str) -> int:
    """Count students assigned to a class."""
    return db.query(DbSinhVien).filter(DbSinhVien.malop == malop).count()


def them_sinhvien(db: Session, request: SinhVienBase) -> DbSinhVien:
    """Insert a student."""
    entity = DbSinhVien(**request.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def sua_sinhvien(
    db: Session,
    entity: DbSinhVien,
    request: SinhVienBase,
) -> DbSinhVien:
    """Persist student changes."""
    for field, value in request.model_dump(exclude={"masv", "password"}).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def xoa_sinhvien(db: Session, entity: DbSinhVien) -> None:
    """Delete a student."""
    db.delete(entity)
    db.commit()


def set_student_class(
    db: Session,
    entity: DbSinhVien,
    malop: str | None,
) -> DbSinhVien:
    """Assign or remove a student's class."""
    entity.malop = malop
    db.commit()
    db.refresh(entity)
    return entity

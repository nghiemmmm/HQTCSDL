"""Exam-registration repository containing database operations only."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from db.model import (
    DbBoDe,
    DbGiaoVien,
    DbGiaoVienDangKy,
    DbLop,
    DbMonHoc,
)
from schemas.schemas import DangKyThi


def get_subject(db: Session, mamh: str) -> DbMonHoc | None:
    """Return a subject."""
    return db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh).first()


def get_class(db: Session, malop: str) -> DbLop | None:
    """Return a class."""
    return db.query(DbLop).filter(DbLop.malop == malop).first()


def get_teacher(db: Session, magv: str) -> DbGiaoVien | None:
    """Return a teacher."""
    return db.query(DbGiaoVien).filter(DbGiaoVien.magv == magv).first()


def get_registration(
    db: Session,
    malop: str,
    mamh: str,
    lan: int,
) -> DbGiaoVienDangKy | None:
    """Return an exam registration by its composite key using SP_GET_GVDK."""
    from sqlalchemy import text
    query = text("EXEC SP_GET_GVDK @MALOP = :malop, @MAMH = :mamh, @LAN = :lan")
    row = db.execute(query, {
        "malop": malop,
        "mamh": mamh,
        "lan": lan
    }).fetchone()
    
    if row is None:
        return None
        
    return DbGiaoVienDangKy(
        magv=row[0],
        malop=row[1],
        mamh=row[2],
        trinhdo=row[3],
        lan=row[4],
        ngaythi=row[5],
        socauthi=row[6],
        thoigian=row[7]
    )


def check_question_count_with_procedure(
    db: Session,
    mamh: str,
    trinhdo: str,
    socauthi: int,
):
    """Execute the existing question-count procedure."""
    return db.execute(
        text(
            "EXEC SP_KiemTraSoLuongCauHoi "
            "@MAMH=:mamh, @TRINHDO=:trinhdo, @SOCAUTHI=:socauthi"
        ),
        {"mamh": mamh, "trinhdo": trinhdo, "socauthi": socauthi},
    ).fetchone()


def count_questions(db: Session, mamh: str, trinhdo: str) -> int:
    """Count questions by subject and level."""
    return db.query(DbBoDe).filter(
        DbBoDe.mamh == mamh,
        DbBoDe.trinhdo == trinhdo,
    ).count()


def create(db: Session, request: DangKyThi) -> DbGiaoVienDangKy:
    """Insert an exam registration."""
    entity = DbGiaoVienDangKy(**request.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_all(db: Session) -> list[DbGiaoVienDangKy]:
    """Return all registrations."""
    return db.query(DbGiaoVienDangKy).all()


def get_by_lop(db: Session, malop: str) -> list[DbGiaoVienDangKy]:
    """Return registrations for a class."""
    return db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.malop == malop
    ).all()


def delete(db: Session, entity: DbGiaoVienDangKy) -> None:
    """Delete a registration."""
    db.delete(entity)
    db.commit()


def get_monhocdk(db: Session, magv: str) -> list[DbMonHoc]:
    """Return distinct subjects registered by a teacher."""
    return db.query(DbMonHoc).join(
        DbGiaoVienDangKy,
        DbMonHoc.mamh == DbGiaoVienDangKy.mamh,
    ).filter(DbGiaoVienDangKy.magv == magv).all()


def list_registrations_in_range(db: Session, from_date: str, to_date: str) -> list:
    """Return exam registrations between two dates using SP_GET_DS_GVDK."""
    query = text("EXEC SP_GET_DS_GVDK @FROM = :from_date, @TO = :to_date")
    return db.execute(query, {"from_date": from_date, "to_date": to_date}).fetchall()

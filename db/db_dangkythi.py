"""Exam-registration repository containing database operations only."""

from sqlalchemy import String, cast, text
from sqlalchemy.orm import Session

from db.model import (
    DbBangDiem,
    DbBoDe,
    DbGiaoVien,
    DbGiaoVienDangKy,
    DbLop,
    DbMonHoc,
    DbPhienThi,
    DbSinhVien,
)
from schemas.schemas import DangKyThi


def get_subject(db: Session, mamh: str) -> DbMonHoc | None:
    """Return a subject."""
    return db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh).first()


def get_all_subjects(db: Session) -> list[DbMonHoc]:
    """Return all subjects."""
    return db.query(DbMonHoc).order_by(DbMonHoc.mamh).all()


def get_class(db: Session, malop: str) -> DbLop | None:
    """Return a class."""
    return db.query(DbLop).filter(DbLop.malop == malop).first()


def get_all_classes(db: Session) -> list[DbLop]:
    """Return all classes."""
    return db.query(DbLop).order_by(DbLop.malop).all()


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


def get_registration_entity(
    db: Session,
    malop: str,
    mamh: str,
    lan: int,
) -> DbGiaoVienDangKy | None:
    """Return a tracked exam-registration entity by its composite key."""
    return db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.malop == malop,
        DbGiaoVienDangKy.mamh == mamh,
        DbGiaoVienDangKy.lan == lan,
    ).first()


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


def update(
    db: Session,
    entity: DbGiaoVienDangKy,
    request: DangKyThi,
) -> DbGiaoVienDangKy:
    """Update an exam registration without changing its business key."""
    entity.magv = request.magv
    entity.trinhdo = request.trinhdo
    entity.ngaythi = request.ngaythi
    entity.socauthi = request.socauthi
    entity.thoigian = request.thoigian
    db.commit()
    db.refresh(entity)
    return entity


def get_all(db: Session) -> list[DbGiaoVienDangKy]:
    """Return all registrations."""
    return db.query(DbGiaoVienDangKy).order_by(
        DbGiaoVienDangKy.ngaythi.desc(),
        DbGiaoVienDangKy.malop,
        DbGiaoVienDangKy.mamh,
        DbGiaoVienDangKy.lan,
    ).all()


def search_registrations(db: Session, keyword: str) -> list[DbGiaoVienDangKy]:
    """Search registrations by class, subject, teacher, level, or attempt."""
    like = f"%{keyword.strip()}%"
    return db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.malop.like(like)
        | DbGiaoVienDangKy.mamh.like(like)
        | DbGiaoVienDangKy.magv.like(like)
        | DbGiaoVienDangKy.trinhdo.like(like)
        | cast(DbGiaoVienDangKy.lan, String).like(like)
    ).order_by(
        DbGiaoVienDangKy.ngaythi.desc(),
        DbGiaoVienDangKy.malop,
        DbGiaoVienDangKy.mamh,
        DbGiaoVienDangKy.lan,
    ).all()


def get_by_lop(db: Session, malop: str) -> list[DbGiaoVienDangKy]:
    """Return registrations for a class."""
    return db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.malop == malop
    ).all()


def get_by_teacher(db: Session, magv: str) -> list[DbGiaoVienDangKy]:
    """Return registrations created by a teacher."""
    return db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.magv == magv
    ).order_by(
        DbGiaoVienDangKy.ngaythi.desc(),
        DbGiaoVienDangKy.malop,
        DbGiaoVienDangKy.mamh,
        DbGiaoVienDangKy.lan,
    ).all()


def has_exam_result(db: Session, malop: str, mamh: str, lan: int) -> bool:
    """Return whether any student in the class has a score for the exam."""
    return db.query(DbBangDiem).join(
        DbSinhVien,
        DbBangDiem.masv == DbSinhVien.masv,
    ).filter(
        DbSinhVien.malop == malop,
        DbBangDiem.mamh == mamh,
        DbBangDiem.lan == lan,
    ).first() is not None


def has_exam_session(db: Session, malop: str, mamh: str, lan: int) -> bool:
    """Return whether any exam session already exists for the registration."""
    return db.query(DbPhienThi).filter(
        DbPhienThi.malop == malop,
        DbPhienThi.mamh == mamh,
        DbPhienThi.lan == lan,
    ).first() is not None


def search_registrations_by_teacher(
    db: Session,
    magv: str,
    keyword: str,
) -> list[DbGiaoVienDangKy]:
    """Search registrations created by a teacher."""
    like = f"%{keyword.strip()}%"
    return db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.magv == magv,
        (
            DbGiaoVienDangKy.malop.like(like)
            | DbGiaoVienDangKy.mamh.like(like)
            | DbGiaoVienDangKy.trinhdo.like(like)
            | cast(DbGiaoVienDangKy.lan, String).like(like)
        ),
    ).order_by(
        DbGiaoVienDangKy.ngaythi.desc(),
        DbGiaoVienDangKy.malop,
        DbGiaoVienDangKy.mamh,
        DbGiaoVienDangKy.lan,
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

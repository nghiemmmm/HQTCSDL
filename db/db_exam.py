"""Exam repository containing all direct persistence operations."""

from datetime import date, datetime, time

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from db.model import (
    DbBangDiem,
    DbBoDe,
    DbGiaoVienDangKy,
    DbLop,
    DbMonHoc,
    DbPhienThi,
    DbSinhVien,
)


def get_student(db: Session, student_id: str) -> DbSinhVien | None:
    """Return one student."""
    return db.query(DbSinhVien).filter(DbSinhVien.masv == student_id).first()


def get_class(db: Session, class_id: str) -> DbLop | None:
    """Return one class."""
    return db.query(DbLop).filter(DbLop.malop == class_id).first()


def get_subject(db: Session, subject_id: str) -> DbMonHoc | None:
    """Return one subject."""
    return db.query(DbMonHoc).filter(DbMonHoc.mamh == subject_id).first()


def list_all_subjects(db: Session) -> list[DbMonHoc]:
    """Return all subjects."""
    return db.query(DbMonHoc).all()


def list_subjects_for_class(db: Session, class_id: str) -> list[DbMonHoc]:
    """Return distinct subjects registered for a class."""
    return (
        db.query(DbMonHoc)
        .join(DbGiaoVienDangKy, DbMonHoc.mamh == DbGiaoVienDangKy.mamh)
        .filter(DbGiaoVienDangKy.malop == class_id)
        .distinct()
        .all()
    )


def get_registration(
    db: Session,
    subject_id: str,
    attempt: int,
    class_id: str,
    exam_date: date,
) -> DbGiaoVienDangKy | None:
    """Return an exam registration matching its business key and date using SP_GET_GVDK."""
    from sqlalchemy import text
    query = text("EXEC SP_GET_GVDK @MALOP = :malop, @MAMH = :mamh, @LAN = :lan")
    row = db.execute(query, {
        "malop": class_id,
        "mamh": subject_id,
        "lan": attempt
    }).fetchone()
    
    if row is None:
        return None
        
    db_date = row[5]
    if db_date:
        # Check if dates match
        if db_date.date() != exam_date:
            return None
            
    return DbGiaoVienDangKy(
        magv=row[0],
        malop=row[1],
        mamh=row[2],
        trinhdo=row[3],
        lan=row[4],
        ngaythi=db_date,
        socauthi=row[6],
        thoigian=row[7]
    )


def list_registrations_for_class(
    db: Session,
    class_id: str,
) -> list[DbGiaoVienDangKy]:
    """Return registrations for a class, newest first."""
    return (
        db.query(DbGiaoVienDangKy)
        .filter(DbGiaoVienDangKy.malop == class_id)
        .order_by(DbGiaoVienDangKy.ngaythi.desc())
        .all()
    )


def get_score(
    db: Session,
    student_id: str,
    subject_id: str,
    attempt: int,
) -> DbBangDiem | None:
    """Return one persisted score."""
    return db.query(DbBangDiem).filter(
        DbBangDiem.masv == student_id,
        DbBangDiem.mamh == subject_id,
        DbBangDiem.lan == attempt,
    ).first()


def get_session(
    db: Session,
    session_id: int,
    student_id: str,
) -> DbPhienThi | None:
    """Return a student-owned exam session."""
    return db.query(DbPhienThi).filter(
        DbPhienThi.id == session_id,
        DbPhienThi.masv == student_id,
    ).first()


def get_latest_session(
    db: Session,
    student_id: str,
    subject_id: str,
    attempt: int,
    class_id: str,
    exam_date: date,
    status: str | None = None,
) -> DbPhienThi | None:
    """Return the latest matching exam session."""
    query = db.query(DbPhienThi).filter(
        DbPhienThi.masv == student_id,
        DbPhienThi.mamh == subject_id,
        DbPhienThi.lan == attempt,
        DbPhienThi.malop == class_id,
        DbPhienThi.ngaythi == exam_date,
    )
    if status:
        query = query.filter(DbPhienThi.trangthai == status)
    return query.order_by(DbPhienThi.id.desc()).first()


def get_latest_submitted_session(
    db: Session,
    student_id: str,
    session_id: int | None = None,
) -> DbPhienThi | None:
    """Return a submitted session owned by a student."""
    query = db.query(DbPhienThi).filter(
        DbPhienThi.masv == student_id,
        DbPhienThi.trangthai == "DA_NOP",
    )
    if session_id is not None:
        query = query.filter(DbPhienThi.id == session_id)
    return query.order_by(
        DbPhienThi.nopbai_luc.desc(),
        DbPhienThi.id.desc(),
    ).first()


def get_random_questions(
    db: Session,
    subject_id: str,
    level: str,
    limit: int,
) -> list[DbBoDe]:
    """Return random questions for a subject and level."""
    return (
        db.query(DbBoDe)
        .filter(DbBoDe.mamh == subject_id, DbBoDe.trinhdo == level)
        .order_by(func.newid())
        .limit(limit)
        .all()
    )


def get_questions_by_ids(
    db: Session,
    question_ids: list[int],
    subject_id: str | None = None,
) -> list[DbBoDe]:
    """Return questions by IDs."""
    if not question_ids:
        return []
    query = db.query(DbBoDe).filter(DbBoDe.cauhoi.in_(question_ids))
    if subject_id:
        query = query.filter(DbBoDe.mamh == subject_id)
    return query.all()


def create_session(db: Session, entity: DbPhienThi) -> DbPhienThi:
    """Insert an exam session."""
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def save_session(db: Session, entity: DbPhienThi) -> DbPhienThi:
    """Persist an exam session."""
    db.commit()
    db.refresh(entity)
    return entity


def submit_exam(
    db: Session,
    score: DbBangDiem,
    session: DbPhienThi,
) -> None:
    """Atomically insert a score and persist the submitted session."""
    db.add(score)
    db.add(session)
    db.commit()


def submit_exam_with_procedure(
    db: Session,
    session_id: int,
    score_value: float,
    answers_json: str,
) -> None:
    """Submit the exam and record the score using SP_INSERT_KQ_THI stored procedure."""
    from sqlalchemy import text
    query = text(
        "EXEC SP_INSERT_KQ_THI "
        "@PHIENTHI_ID = :phienthi_id, @DIEM = :diem, @DAPAN_DACHON = :dapan_dachon"
    )
    db.execute(
        query,
        {
            "phienthi_id": session_id,
            "diem": score_value,
            "dapan_dachon": answers_json,
        },
    )


def has_student_taken_exam(
    db: Session,
    student_id: str,
    subject_id: str,
    attempt: int,
) -> bool:
    """Check if a student has taken an exam for a subject and attempt using SP_KT_Lan_Thi."""
    from sqlalchemy import text
    query = text("EXEC SP_KT_Lan_Thi @MASV = :masv, @MAMH = :mamh, @LAN = :lan")
    row = db.execute(query, {
        "masv": student_id,
        "mamh": subject_id,
        "lan": attempt
    }).fetchone()
    
    if row and row[0] == '1':
        return True
    return False


def get_student_subjects_taken(db: Session, student_id: str) -> list:
    """Return subjects a student has taken using SP_GET_MH_DATHI_SV."""
    from sqlalchemy import text
    query = text("EXEC SP_GET_MH_DATHI_SV @MASV = :masv")
    return db.execute(query, {"masv": student_id}).fetchall()


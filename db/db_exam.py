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


def list_classes_by_teacher(db: Session, teacher_id: str) -> list[DbLop]:
    """Return distinct classes for which a teacher has created exam registrations."""
    return (
        db.query(DbLop)
        .join(DbGiaoVienDangKy, DbLop.malop == DbGiaoVienDangKy.malop)
        .filter(DbGiaoVienDangKy.magv == teacher_id.strip())
        .distinct()
        .order_by(DbLop.malop.asc())
        .all()
    )


def list_subjects_by_teacher(db: Session, teacher_id: str) -> list[DbMonHoc]:
    """Return distinct subjects for which a teacher has created exam registrations."""
    return (
        db.query(DbMonHoc)
        .join(DbGiaoVienDangKy, DbMonHoc.mamh == DbGiaoVienDangKy.mamh)
        .filter(DbGiaoVienDangKy.magv == teacher_id.strip())
        .distinct()
        .order_by(DbMonHoc.tenmh.asc())
        .all()
    )


def list_registrations_by_teacher(db: Session, teacher_id: str) -> list:
    """Return all exam registrations for a teacher with subject and class info, newest first."""
    from sqlalchemy import desc
    rows = (
        db.query(DbGiaoVienDangKy, DbMonHoc, DbLop)
        .join(DbMonHoc, DbGiaoVienDangKy.mamh == DbMonHoc.mamh)
        .join(DbLop, DbGiaoVienDangKy.malop == DbLop.malop)
        .filter(DbGiaoVienDangKy.magv == teacher_id.strip())
        .order_by(desc(DbGiaoVienDangKy.ngaythi))
        .all()
    )
    return [
        {
            "malop": (reg.malop or "").strip(),
            "tenlop": (lop.tenlop or "").strip(),
            "mamh": (reg.mamh or "").strip(),
            "tenmh": (mh.tenmh or "").strip(),
            "lan": reg.lan,
            "ngaythi": reg.ngaythi.strftime("%d/%m/%Y") if reg.ngaythi else "",
            "ngaythi_sort": reg.ngaythi.isoformat() if reg.ngaythi else "",
        }
        for reg, mh, lop in rows
    ]


def list_exam_schedules_for_student(db: Session, student_id: str) -> list:
    """Return exam schedules for a student by passing the exact raw query."""
    from sqlalchemy import text
    query = text("""
        DECLARE @Today DATE = CAST(GETDATE() AS DATE);
        SELECT
            MAMH = RTRIM(GVDK.MAMH),
            TENMH = MH.TENMH,
            LAN = GVDK.LAN,
            NGAYTHI = GVDK.NGAYTHI,
            SOCAUTHI = GVDK.SOCAUTHI,
            THOIGIAN = GVDK.THOIGIAN,
            TRANGTHAI =
                CASE
                    WHEN BD.MASV IS NOT NULL
                        THEN N'Đã thi'
                    WHEN CAST(GVDK.NGAYTHI AS DATE) > @Today
                        THEN N'Chưa đến ngày thi'
                    WHEN CAST(GVDK.NGAYTHI AS DATE) = @Today
                        THEN N'Được thi hôm nay'
                    ELSE N'Đã quá hạn'
                END,
            DUOC_BAT_DAU_THI =
                CONVERT(bit,
                    CASE
                        WHEN BD.MASV IS NULL
                             AND CAST(GVDK.NGAYTHI AS DATE) = @Today
                        THEN 1
                        ELSE 0
                    END
                )
        FROM SINHVIEN SV
        INNER JOIN GIAOVIEN_DANGKY GVDK
            ON GVDK.MALOP = SV.MALOP
        INNER JOIN MONHOC MH
            ON MH.MAMH = GVDK.MAMH
        LEFT JOIN BANGDIEM BD
            ON BD.MASV = SV.MASV
           AND BD.MAMH = GVDK.MAMH
           AND BD.LAN = GVDK.LAN
        WHERE SV.MASV = :masv
        ORDER BY GVDK.NGAYTHI DESC, GVDK.MAMH, GVDK.LAN;
    """)
    return db.execute(query, {"masv": student_id}).fetchall()


def get_registration(
    db: Session,
    subject_id: str,
    attempt: int,
    class_id: str,
    exam_date: date,
) -> DbGiaoVienDangKy | None:
    """Return an exam registration matching its business key and date."""
    reg = (
        db.query(DbGiaoVienDangKy)
        .filter(
            DbGiaoVienDangKy.malop == class_id,
            DbGiaoVienDangKy.mamh == subject_id,
            DbGiaoVienDangKy.lan == attempt,
        )
        .first()
    )
    if reg is None:
        return None
    if reg.ngaythi and reg.ngaythi.date() != exam_date:
        return None
    return reg


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

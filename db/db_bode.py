"""Question repository containing persistence operations only."""

from sqlalchemy.orm import Session

from db.model import DbBoDe
from schemas.schemas import CauHoiCreate, CauHoiUpdate


def get_all_bode(db: Session) -> list[DbBoDe]:
    """Return all questions."""
    return db.query(DbBoDe).all()


def get_by_teacher(db: Session, teacher_id: str) -> list[DbBoDe]:
    """Return questions owned by a teacher."""
    return db.query(DbBoDe).filter(DbBoDe.magv == teacher_id).all()


def get_by_id(db: Session, question_id: int) -> DbBoDe | None:
    """Return one question."""
    return db.query(DbBoDe).filter(DbBoDe.cauhoi == question_id).first()


def create_bode(db: Session, request: CauHoiCreate) -> DbBoDe:
    """Insert a question."""
    question = DbBoDe(**request.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def update_bode(
    db: Session,
    question: DbBoDe,
    request: CauHoiUpdate,
) -> DbBoDe:
    """Persist changes to a question using SP_Phuc_Hoi_Sua_Bo_De."""
    mamh = request.mamh if request.mamh is not None else question.mamh
    magv = request.magv if request.magv is not None else question.magv
    trinhdo = request.trinhdo if request.trinhdo is not None else question.trinhdo
    dapan = request.dap_an if request.dap_an is not None else question.dap_an
    noidung = request.noidung if request.noidung is not None else question.noidung
    a = request.a if request.a is not None else question.a
    b = request.b if request.b is not None else question.b
    c = request.c if request.c is not None else question.c
    d = request.d if request.d is not None else question.d

    from sqlalchemy import text
    query = text(
        "EXEC SP_Phuc_Hoi_Sua_Bo_De "
        "@MACH = :mach, @MAMH = :mamh, @MAGV = :magv, @TRINHDO = :trinhdo, "
        "@DAPAN = :dapan, @NOIDUNG = :noidung, @A = :a, @B = :b, @C = :c, @D = :d"
    )
    db.execute(
        query,
        {
            "mach": question.cauhoi,
            "mamh": mamh,
            "magv": magv,
            "trinhdo": trinhdo,
            "dapan": dapan,
            "noidung": noidung,
            "a": a,
            "b": b,
            "c": c,
            "d": d,
        },
    )
    db.commit()
    db.refresh(question)
    return question


def delete_bode(db: Session, question: DbBoDe) -> None:
    """Delete a question."""
    db.delete(question)
    db.commit()

"""Business operations for the question bank."""

import json
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_bode, db_giaovien
from db.model import DbBoDe, DbPhienThi
from schemas.schemas import BoDeDisplay, CauHoiCreate, CauHoiUpdate
from services.exceptions import PermissionDeniedError, RepositoryError, ResourceNotFoundError


def _owned_question(db: Session, question_id: int, user: dict[str, Any]) -> DbBoDe:
    question = db_bode.get_by_id(db, question_id)
    if question is None:
        raise ResourceNotFoundError(f"Khong tim thay cau hoi voi id {question_id}")
    if (
        user.get("role") == "GIANGVIEN"
        and (question.magv or "").strip() != (user.get("ma") or "").strip()
    ):
        raise PermissionDeniedError("Khong duoc thao tac cau hoi cua giao vien khac")
    return question



def _question_payload(question: DbBoDe) -> dict[str, Any]:
    return {
        "cauhoi": question.cauhoi,
        "mamh": (question.mamh or "").strip(),
        "trinhdo": (question.trinhdo or "").strip(),
        "noidung": question.noidung or "",
        "a": question.a or "",
        "b": question.b or "",
        "c": question.c or "",
        "d": question.d or "",
        "dap_an": (question.dap_an or "").strip(),
        "magv": (question.magv or "").strip(),
    }
def get_page_data(db: Session, user: dict[str, Any]) -> dict[str, list]:
    """Build the question-page data while enforcing teacher ownership."""
    questions = (
        db_bode.get_by_teacher(db, user.get("ma", ""))
        if user.get("role") == "GIANGVIEN"
        else db_bode.get_all_bode(db)
    )
    teachers = db_giaovien.get_all(db)
    return {
        "bodes": [_question_payload(item) for item in questions],
        "giaoviens": [
            {
                "magv": (teacher.magv or "").strip(),
                "hoten": (
                    f"{(teacher.ho or '').strip()} {(teacher.ten or '').strip()}"
                ).strip(),
            }
            for teacher in teachers
        ],
    }


def create_question(
    db: Session,
    request: CauHoiCreate,
    user: dict[str, Any],
) -> DbBoDe:
    """Create a question, assigning teachers to their own records."""
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma", "")
    try:
        return db_bode.create_bode(db, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc


def _contains_question_id(value: Any, question_id: int) -> bool:
    if isinstance(value, dict):
        for key in ("cauhoi", "id", "question_id"):
            if str(value.get(key, "")).strip() == str(question_id):
                return True
        return any(_contains_question_id(item, question_id) for item in value.values())
    if isinstance(value, list):
        return any(_contains_question_id(item, question_id) for item in value)
    return str(value).strip() == str(question_id)


def get_question_status(
    db: Session,
    question_id: int,
    user: dict[str, Any],
) -> dict[str, bool]:
    """Return whether a question has already been used in an exam session."""
    _owned_question(db, question_id, user)
    for exam_session in db.query(DbPhienThi.danhsach_cauhoi).all():
        raw_value = exam_session[0]
        try:
            question_list = json.loads(raw_value or "[]")
        except (TypeError, json.JSONDecodeError):
            question_list = raw_value
        if _contains_question_id(question_list, question_id):
            return {"da_su_dung": True}
    return {"da_su_dung": False}


def update_question(
    db: Session,
    question_id: int,
    request: CauHoiUpdate,
    user: dict[str, Any],
) -> DbBoDe:
    """Update a question after ownership validation."""
    question = _owned_question(db, question_id, user)
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma", "")
    try:
        return db_bode.update_bode(db, question, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc


def delete_question(
    db: Session,
    question_id: int,
    user: dict[str, Any],
) -> dict[str, str]:
    """Delete a question after ownership validation."""
    question = _owned_question(db, question_id, user)
    try:
        db_bode.delete_bode(db, question)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {"message": "Xóa câu hỏi thành công!"}

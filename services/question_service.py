"""Business operations for the question bank."""

from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_bode, db_giaovien
from db.model import DbBoDe
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


def get_page_data(db: Session, user: dict[str, Any]) -> dict[str, list]:
    """Build the question-page data while enforcing teacher ownership."""
    questions = (
        db_bode.get_by_teacher(db, user.get("ma", ""))
        if user.get("role") == "GIANGVIEN"
        else db_bode.get_all_bode(db)
    )
    teachers = db_giaovien.get_all(db)
    return {
        "bodes": [
            BoDeDisplay.model_validate(item).model_dump()
            for item in questions
        ],
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

"""Business operations for classes."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_lop
from db.model import DbLop
from schemas.schemas import LopDisplay
from services.exceptions import ConflictError, RepositoryError, ResourceNotFoundError, ValidationError


def list_classes(db: Session) -> list[DbLop]:
    """Return all classes."""
    return db_lop.get_all_lop(db)


def get_class(db: Session, malop: str) -> DbLop:
    """Return a class or raise not found."""
    entity = db_lop.get_by_id(db, malop.strip())
    if entity is None:
        raise ResourceNotFoundError(
            {"message": f"Khong tim thay lop co ma: {malop.strip()}"}
        )
    return entity


def create_class(db: Session, request: LopDisplay) -> DbLop:
    """Create a class after validating unique code and name."""
    code, name = request.malop.strip(), request.tenlop.strip()
    if not code or not name:
        raise ValidationError({"message": "Ma lop va ten lop khong duoc de trong"})
    status = db_lop.check_class_existence(db, code, name)
    if status == 1:
        raise ConflictError({"message": f"Ma lop {code} da ton tai"})
    elif status == 2:
        raise ConflictError({"message": f"Ten lop {name} da ton tai"})
    request.malop, request.tenlop = code, name
    try:
        return db_lop.them_lop(db, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError({"message": f"Loi khi them lop: {exc}"}) from exc


def update_class(db: Session, malop: str, request: LopDisplay) -> DbLop:
    """Update a class name."""
    entity = get_class(db, malop)
    name = request.tenlop.strip()
    if not name:
        raise ValidationError({"message": "Ten lop khong duoc de trong"})
    duplicate = db_lop.get_by_name(db, name)
    if duplicate and duplicate.malop != entity.malop:
        raise ConflictError({"message": f"Ten lop {name} da ton tai"})
    request.tenlop = name
    try:
        return db_lop.sua_lop(db, entity, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError({"message": f"Loi khi sua lop: {exc}"}) from exc


def delete_class(db: Session, malop: str) -> dict[str, str]:
    """Delete an empty class."""
    entity = get_class(db, malop)
    count = db_lop.count_students(db, malop)
    if count:
        raise ConflictError({"message": f"Khong the xoa lop co {count} sinh vien"})
    try:
        db_lop.xoa_lop(db, entity)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError({"message": f"Loi khi xoa lop: {exc}"}) from exc
    return {"message": f"Xóa lớp {malop} thành công"}

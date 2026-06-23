"""Business operations for students."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_lop, db_sinhvien
from db.model import DbSinhVien
from schemas.schemas import SinhVienBase
from services.exceptions import ConflictError, RepositoryError, ResourceNotFoundError, ValidationError


def get_student(db: Session, masv: str) -> DbSinhVien:
    """Return a student or raise not found."""
    entity = db_sinhvien.get_by_id(db, masv.strip())
    if entity is None:
        raise ResourceNotFoundError(
            {"message": f"Khong tim thay sinh vien co ma: {masv.strip()}"}
        )
    return entity


def list_students_by_class(db: Session, malop: str) -> list[DbSinhVien]:
    """Return students after validating the class exists."""
    code = malop.strip()
    if not code:
        raise ValidationError({"message": "Ma lop khong duoc de trong"})
    if db_lop.get_by_id(db, code) is None:
        raise ResourceNotFoundError({"message": f"Khong tim thay lop co ma: {code}"})
    return db_sinhvien.lay_ds_sinh_vien_mot_lop(db, code)


def create_student(db: Session, request: SinhVienBase) -> DbSinhVien:
    """Create a unique student assigned to an existing class."""
    code = request.masv.strip()
    if not code:
        raise ValidationError({"message": "Ma sinh vien khong duoc de trong"})
    if db_sinhvien.get_by_id(db, code):
        raise ConflictError({"message": f"Ma sinh vien {code} da ton tai"})
    if request.malop and db_lop.get_by_id(db, request.malop) is None:
        raise ResourceNotFoundError(
            {"message": f"Khong tim thay lop co ma: {request.malop}"}
        )
    request.masv = code
    try:
        return db_sinhvien.them_sinhvien(db, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError({"message": f"Loi khi them sinh vien: {exc}"}) from exc


def update_student(db: Session, masv: str, request: SinhVienBase) -> DbSinhVien:
    """Update student profile and class assignment."""
    entity = get_student(db, masv)
    if request.malop and db_lop.get_by_id(db, request.malop) is None:
        raise ResourceNotFoundError(
            {"message": f"Khong tim thay lop co ma: {request.malop}"}
        )
    try:
        return db_sinhvien.sua_sinhvien(db, entity, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError({"message": f"Loi khi sua sinh vien: {exc}"}) from exc


def delete_student(db: Session, masv: str) -> dict[str, str]:
    """Delete a student."""
    entity = get_student(db, masv)
    try:
        db_sinhvien.xoa_sinhvien(db, entity)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError({"message": f"Loi khi xoa sinh vien: {exc}"}) from exc
    return {"message": f"Xóa sinh viên {masv} thành công"}

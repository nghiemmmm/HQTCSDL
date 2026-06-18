"""Business operations for teachers."""

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_giaovien
from db.model import DbGiaoVien
from schemas.schemas import GiaoVienCreate, GiaoVienUpdate, GiaoVienPublic
from services.exceptions import ConflictError, RepositoryError, ResourceNotFoundError


def _payload(teacher: DbGiaoVien) -> dict:
    return {
        "magv": teacher.magv,
        "ho": teacher.ho,
        "ten": teacher.ten,
        "diachi": teacher.diachi,
        "sodtll": teacher.sodtll,
    }


def list_teachers(db: Session) -> list[DbGiaoVien]:
    """Return all teachers."""
    return db_giaovien.get_all(db)


def list_teacher_displays(db: Session) -> list[GiaoVienPublic]:
    """Return all teachers serialized for the API."""
    return [GiaoVienPublic.model_validate(row) for row in db_giaovien.get_all_gv(db)]


def list_unregistered_teachers(db: Session) -> list[GiaoVienPublic]:
    """Return teachers without a system account."""
    return [
        GiaoVienPublic(
            magv=(row.MAGV or "").strip(),
            ho=(getattr(row, "HO", None) or "").strip() or None,
            ten=(getattr(row, "TEN", None) or "").strip() or None,
            diachi=None,
            sodtll=None,
        )
        for row in db_giaovien.get_ds_gv_chua_quyen(db)
    ]


def list_registration_candidates(db: Session) -> list[dict]:
    """Return stored-procedure fields used by the registration template."""
    return [
        {
            "magv": getattr(row, "MAGV", None),
            "hoten": getattr(row, "HOTEN", None)
            or (
                f"{getattr(row, 'HO', '') or ''} "
                f"{getattr(row, 'TEN', '') or ''}"
            ).strip(),
            "trangthai": getattr(row, "TRANGTHAI", None),
        }
        for row in db_giaovien.get_ds_gv_chua_quyen(db)
    ]


def get_teacher(db: Session, magv: str) -> DbGiaoVien:
    """Return one teacher or raise not found."""
    teacher = db_giaovien.get_by_id(db, magv)
    if teacher is None:
        raise ResourceNotFoundError(f"Không tìm thấy giáo viên {magv}")
    return teacher


def create_teacher(db: Session, request: GiaoVienCreate) -> dict:
    """Create a unique teacher."""
    if db_giaovien.get_by_id(db, request.magv):
        raise ConflictError(f"Mã giáo viên {request.magv} đã tồn tại")
    try:
        teacher = db_giaovien.create(db, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {
        "message": (
            f"Thêm thành công giáo viên: "
            f"{(teacher.ho or '')} {(teacher.ten or '')}"
        ).strip(),
        "data": _payload(teacher),
    }


def update_teacher(db: Session, magv: str, request: GiaoVienUpdate) -> dict:
    """Update a teacher."""
    teacher = get_teacher(db, magv)
    try:
        teacher = db_giaovien.update(db, teacher, request)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {
        "message": (
            f"Sửa thành công giáo viên: "
            f"{(teacher.ho or '')} {(teacher.ten or '')}"
        ).strip(),
        "data": _payload(teacher),
    }


def delete_teacher(db: Session, magv: str) -> dict[str, str]:
    """Delete a teacher when database constraints allow it."""
    teacher = get_teacher(db, magv)
    name = f"{(teacher.ho or '')} {(teacher.ten or '')}".strip()
    try:
        db_giaovien.delete(db, teacher)
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "Không thể xóa giáo viên này do ràng buộc dữ liệu."
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(str(exc)) from exc
    return {"message": f"Xóa thành công giáo viên: {name}"}


def search_teachers(db: Session, keyword: str) -> list[DbGiaoVien]:
    """Search teachers, returning all when no keyword is provided."""
    return db_giaovien.search(db, keyword) if keyword else list_teachers(db)

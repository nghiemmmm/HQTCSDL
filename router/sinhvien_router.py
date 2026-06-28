"""HTTP routes for student management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from core.templates import Jinja2Templates
from sqlalchemy import func

from db.model import DbBangDiem, DbGiaoVienDangKy, DbPhienThi
from db.roles import Permission
from router.dependencies import DatabaseDep, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import Message, SinhVienBase, SinhVienDisplay, SinhVienWithLopDisplay
from services import student_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/sinhvien", tags=["Sinhvien"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def hien_thi_mon_hoc(
    request: Request,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_STUDENT))],
):
    """Render the student management page."""
    return templates.TemplateResponse(
        "formSinhVien.html",
        {"request": request, "user": user, "page_mode": "student"},
    )


@router.get("/lop/{malop}", response_model=list[SinhVienWithLopDisplay])
def get_sinh_vien_by_lop(
    malop: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_STUDENT))],
):
    """Return students in a class."""
    try:
        return student_service.list_students_by_class(db, malop)
    except ServiceError as exc:
        raise_http_error(exc)


@router.post("/", response_model=SinhVienDisplay)
def create_sinh_vien(
    sinhvien: SinhVienBase,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.CREATE_STUDENT))],
):
    """Create a student."""
    try:
        return student_service.create_student(db, sinhvien)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/{masv}/check-status")
def check_status(
    masv: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_STUDENT))],
):
    """Return whether the student already has exam data or registrations."""
    try:
        student = student_service.get_student(db, masv)
        code = masv.strip()
        class_code = (student.malop or "").strip()
        da_thi = (
            db.query(DbBangDiem)
            .filter(func.trim(DbBangDiem.masv) == code)
            .first()
            is not None
        )
        co_phien_thi = (
            db.query(DbPhienThi)
            .filter(func.trim(DbPhienThi.masv) == code)
            .first()
            is not None
        )
        da_dang_ky = False
        if class_code:
            da_dang_ky = (
                db.query(DbGiaoVienDangKy)
                .filter(func.trim(DbGiaoVienDangKy.malop) == class_code)
                .first()
                is not None
            )
        return {"da_thi": da_thi or co_phien_thi, "da_dang_ky": da_dang_ky}
    except ServiceError as exc:
        raise_http_error(exc)


@router.put("/{masv}", response_model=SinhVienDisplay)
def update_sinh_vien(
    masv: str,
    sinhvien: SinhVienBase,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.UPDATE_STUDENT))],
):
    """Update a student."""
    try:
        return student_service.update_student(db, masv, sinhvien)
    except ServiceError as exc:
        raise_http_error(exc)


@router.delete("/{masv}", response_model=Message)
def delete_sinh_vien(
    masv: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.DELETE_STUDENT))],
):
    """Delete a student."""
    try:
        return student_service.delete_student(db, masv)
    except ServiceError as exc:
        raise_http_error(exc)

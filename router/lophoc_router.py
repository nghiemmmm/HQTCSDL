"""HTTP routes for class management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from core.templates import Jinja2Templates

from db.roles import Permission
from router.dependencies import DatabaseDep, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import LopDisplay, Message, SinhVienWithLopDisplay
from services import class_service, student_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/lop", tags=["Lop"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def hien_thi_sinh_vien(
    request: Request,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_CLASS))],
):
    """Render the class and student page."""
    return templates.TemplateResponse(
        "formSinhVien.html",
        {"request": request, "user": user, "page_mode": "class"},
    )


@router.get("/lophoc", response_model=list[LopDisplay])
def get_all_lophoc(
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_CLASS))],
):
    """Return all classes."""
    return class_service.list_classes(db)


@router.post("/", response_model=LopDisplay)
def them_lop_moi(
    lop: LopDisplay,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.CREATE_CLASS))],
):
    """Create a class."""
    try:
        return class_service.create_class(db, lop)
    except ServiceError as exc:
        raise_http_error(exc)


@router.put("/{malop}", response_model=LopDisplay)
def sua_lop_existing(
    malop: str,
    lop: LopDisplay,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.UPDATE_CLASS))],
):
    """Update a class."""
    try:
        return class_service.update_class(db, malop, lop)
    except ServiceError as exc:
        raise_http_error(exc)


@router.delete("/{malop}", response_model=Message)
def xoa_lop_existing(
    malop: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.DELETE_CLASS))],
):
    """Delete a class."""
    try:
        return class_service.delete_class(db, malop)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/{malop}", response_model=list[SinhVienWithLopDisplay])
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

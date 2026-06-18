"""HTTP routes for teacher management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.roles import Permission
from router.dependencies import DatabaseDep, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import GiaoVienCreate, GiaoVienUpdate, GiaoVienPublic, Message
from services import teacher_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/giaovien", tags=["GiaoVien"])
templates = Jinja2Templates(directory="templates")


@router.get("/GVCHDK")
def get_giao_vien(
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_TEACHER))],
):
    """Return teachers."""
    try:
        return teacher_service.list_teacher_displays(db)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/GV_CHUA_QUYEN")
def get_giao_vien_chua_quyen(
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_TEACHER))],
):
    """Return teachers without accounts."""
    try:
        return teacher_service.list_unregistered_teachers(db)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("", response_class=HTMLResponse)
def form_giaovien(
    request: Request,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_TEACHER))],
):
    """Render the teacher page."""
    teachers = teacher_service.list_teachers(db)
    data = [
        {
            "magv": item.magv,
            "ho": item.ho,
            "ten": item.ten,
            "diachi": item.diachi,
            "sodtll": item.sodtll,
        }
        for item in teachers
    ]
    return templates.TemplateResponse(
        "formGiaoVien.html",
        {"request": request, "user": user, "giao_viens": data},
    )


@router.get("/{magv}")
def get_one(
    magv: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_TEACHER))],
):
    """Return one teacher."""
    try:
        return teacher_service.get_teacher(db, magv)
    except ServiceError as exc:
        raise_http_error(exc)


@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    request: GiaoVienCreate,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.CREATE_TEACHER))],
):
    """Create a teacher."""
    try:
        return teacher_service.create_teacher(db, request)
    except ServiceError as exc:
        raise_http_error(exc)


@router.put("/{magv}")
def update(
    magv: str,
    request: GiaoVienUpdate,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.UPDATE_TEACHER))],
):
    """Update a teacher."""
    try:
        return teacher_service.update_teacher(db, magv, request)
    except ServiceError as exc:
        raise_http_error(exc)


@router.delete("/{magv}", response_model=Message)
def delete(
    magv: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.DELETE_TEACHER))],
):
    """Delete a teacher."""
    try:
        return teacher_service.delete_teacher(db, magv)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/search/{keyword}")
def search(
    keyword: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_TEACHER))],
):
    """Search teachers."""
    try:
        return teacher_service.search_teachers(db, keyword)
    except ServiceError as exc:
        raise_http_error(exc)

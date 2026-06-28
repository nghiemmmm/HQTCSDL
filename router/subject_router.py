"""HTTP routes for subject management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from core.templates import Jinja2Templates
from sqlalchemy import func

from db.model import DbGiaoVienDangKy
from db.roles import Permission
from router.dependencies import DatabaseDep, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import MonHocBase, MonHocDisplay
from services import subject_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/monhoc", tags=["MonHoc"])
templates = Jinja2Templates(directory="templates")


def _handle(action):
    try:
        return action()
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("", response_class=HTMLResponse)
def form_monhoc(
    request: Request,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_SUBJECT))],
):
    """Render the subject management page."""
    return templates.TemplateResponse(
        "formMonHoc.html", {"request": request, "user": user}
    )


@router.get("/danhsachMH", response_model=list[MonHocDisplay])
def get_all_monhoc(
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_SUBJECT))],
):
    """Return all subjects."""
    return _handle(lambda: subject_service.list_subjects(db))


@router.get("/search/{keyword}")
def search(
    keyword: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_SUBJECT))],
):
    """Search subjects."""
    return _handle(lambda: subject_service.search_subjects(db, keyword))


@router.get("/{mamh}/check-status")
def check_status(
    mamh: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_SUBJECT))],
):
    """Return whether the subject is already used by an exam registration."""
    def action():
        subject_service.get_subject(db, mamh)
        registered = (
            db.query(DbGiaoVienDangKy)
            .filter(func.trim(DbGiaoVienDangKy.mamh) == mamh.strip())
            .first()
            is not None
        )
        return {"da_dangky_thi": registered}

    return _handle(action)


@router.get("/{mamh}")
def get_one(
    mamh: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_SUBJECT))],
):
    """Return one subject."""
    return _handle(lambda: subject_service.get_subject(db, mamh))


@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    request: MonHocBase,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.CREATE_SUBJECT))],
):
    """Create a subject."""
    return _handle(lambda: subject_service.create_subject(db, request))


@router.put("/{mamh}")
def update(
    mamh: str,
    request: MonHocBase,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.UPDATE_SUBJECT))],
):
    """Update a subject."""
    return _handle(lambda: subject_service.update_subject(db, mamh, request))


@router.delete("/{mamh}")
def delete(
    mamh: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.DELETE_SUBJECT))],
):
    """Delete a subject."""
    return _handle(lambda: subject_service.delete_subject(db, mamh))

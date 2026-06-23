"""HTTP routes for question-bank management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from db.roles import Permission
from router.dependencies import DatabaseDep, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import BoDeDisplay, CauHoiCreate, CauHoiUpdate, Message
from services import question_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/bode", tags=["bode"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def get_bode_page(
    request: Request,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_QUESTION))],
):
    """Render the question bank page."""
    try:
        page_data = question_service.get_page_data(db, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return templates.TemplateResponse(
        "formBoDe.html",
        {"request": request, "user": user, **page_data},
    )


@router.post("/", response_model=BoDeDisplay)
def create_bode(
    request: CauHoiCreate,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.CREATE_QUESTION))],
):
    """Create a question."""
    try:
        question = question_service.create_question(db, request, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Thêm câu hỏi thành công!",
            "data": BoDeDisplay.model_validate(question).model_dump(),
        },
    )


@router.put("/{id}", response_model=BoDeDisplay)
def update_bode(
    id: int,
    request: CauHoiUpdate,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.UPDATE_QUESTION))],
):
    """Update a question."""
    try:
        question = question_service.update_question(db, id, request, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật câu hỏi thành công!",
            "data": BoDeDisplay.model_validate(question).model_dump(),
        },
    )


@router.delete("/{id}", response_model=Message)
def delete_bode(
    id: int,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.DELETE_QUESTION))],
):
    """Delete a question."""
    try:
        result = question_service.delete_question(db, id, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

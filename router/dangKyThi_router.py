from typing import List

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from core.templates import Jinja2Templates
from sqlalchemy.orm.session import Session
from db.database import get_db
from db import db_lop, db_sinhvien, db_dangkythi
from schemas.schemas import DangKyThi, MonHocBase, MonHocDisplay
from core.auth import require_permission
from db.roles import Permission

router = APIRouter(
    prefix="/dangkythi",
    tags=["DangKyThi"]
)
templates = Jinja2Templates(directory="templates")



@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    request: DangKyThi,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.CREATE_EXAM_REGISTRATION)),
):
    return db_dangkythi.create(db, request)

@router.get("", response_class=HTMLResponse)
def read_root(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
):

    return templates.TemplateResponse("formDangKyThi.html", {"request": request, "user": user})
@router.get("/monhocdk", response_model=List[MonHocDisplay])
def get_monhoc_dangky(
    magv: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
):
    return db_dangkythi.get_monhocdk(db, magv)

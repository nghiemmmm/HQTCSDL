from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from schemas.schemas import UserBase, DangNhap, GiaoVien
from db.database import get_db
from db import db_giaovien, db_user 
from core.auth import require_permission
from db.roles import Permission
router = APIRouter(
    prefix = "/giaovien",
    tags= ["GiaoVien"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/GVCHDK")
def get_giao_vien(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_TEACHER)),
):
    return db_giaovien.get_all_gv(db=db)


@router.get("/GV_CHUA_QUYEN")
def get_giao_vien_chua_quyen(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_TEACHER)),
):
    return db_giaovien.get_ds_gv_chua_quyen(db=db)

@router.get("", response_class=HTMLResponse)
def form_giaovien(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_TEACHER)),
):
    giao_viens = db_giaovien.get_all(db)
    giao_viens_json = [
        {
            "magv": gv.magv,
            "ho": gv.ho,
            "ten": gv.ten,
            "diachi": gv.diachi,
            "sodtll": gv.sodtll
        }
        for gv in giao_viens
    ]
    return templates.TemplateResponse(
        "formGiaoVien.html",
        {
            "request": request,
            "giao_viens": giao_viens_json
        }
    )


@router.get("/{magv}")
def get_one(
    magv: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_TEACHER)),
):
    return db_giaovien.get_by_id(db, magv)

@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    request: GiaoVien,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.CREATE_TEACHER)),
):
    return db_giaovien.create(db, request)

@router.put("/{magv}")
def update(
    magv: str,
    request: GiaoVien,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.UPDATE_TEACHER)),
):
    return db_giaovien.update(db, magv, request)

@router.delete("/{magv}")
def delete(
    magv: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.DELETE_TEACHER)),
):
    return db_giaovien.delete(db, magv)

@router.get("/search/{keyword}")
def search(
    keyword: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_TEACHER)),
):
    return db_giaovien.search(db, keyword)

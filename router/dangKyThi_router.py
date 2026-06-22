from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm.session import Session

from core.auth import require_permission
from core.templates import Jinja2Templates
from db import db_dangkythi, db_lop, db_monhoc
from db.database import get_db
from db.model import DbGiaoVienDangKy, DbLop, DbMonHoc
from db.roles import Permission
from schemas.schemas import DangKyThi, LopDisplay, MonHocDisplay

router = APIRouter(
    prefix="/dangkythi",
    tags=["DangKyThi"],
)
templates = Jinja2Templates(directory="templates")


def _owned_magv(user) -> Optional[str]:
    return user.get("ma") if user.get("role") == "GIANGVIEN" else None

def _ensure_registration_owner(db: Session, user, malop: str, mamh: str, lan: int) -> None:
    if user.get("role") != "GIANGVIEN":
        return

    registration = db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.malop == malop,
        DbGiaoVienDangKy.mamh == mamh,
        DbGiaoVienDangKy.lan == lan,
    ).first()
    if registration and (registration.magv or "").strip() != (user.get("ma") or "").strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong duoc sua/xoa lich thi cua giao vien khac",
        )

@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    request: DangKyThi,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.CREATE_EXAM_REGISTRATION)),
):
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma")
    return db_dangkythi.create(db, request)


@router.get("", response_class=HTMLResponse)
def read_root(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
):
    return templates.TemplateResponse("formDangKyThi.html", {"request": request, "user": user})



@router.get("/lophoc", response_model=List[LopDisplay])
def get_lop_dangky(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
):
    return db.query(DbLop).order_by(DbLop.malop).all()


@router.get("/monhoc", response_model=List[MonHocDisplay])
def get_monhoc_all_dangky(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
):
    return db.query(DbMonHoc).order_by(DbMonHoc.mamh).all()

@router.get("/api")
def get_registrations(
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
):
    rows = db_dangkythi.get_all(db, keyword=keyword, magv=_owned_magv(user))
    return [
        {
            "magv": (item.magv or "").strip(),
            "mamh": (item.mamh or "").strip(),
            "malop": (item.malop or "").strip(),
            "trinhdo": (item.trinhdo or "").strip(),
            "ngaythi": item.ngaythi.isoformat() if item.ngaythi else None,
            "ngaythi_text": item.ngaythi.strftime("%d/%m/%Y %H:%M") if item.ngaythi else "",
            "lan": item.lan,
            "socauthi": item.socauthi,
            "thoigian": item.thoigian,
        }
        for item in rows
    ]


@router.put("/{malop}/{mamh}/{lan}")
def update(
    malop: str,
    mamh: str,
    lan: int,
    request: DangKyThi,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.UPDATE_EXAM_REGISTRATION)),
):
    _ensure_registration_owner(db, user, malop, mamh, lan)
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma")
    return db_dangkythi.update(db, malop, mamh, lan, request)


@router.delete("/{malop}/{mamh}/{lan}")
def delete(
    malop: str,
    mamh: str,
    lan: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.DELETE_EXAM_REGISTRATION)),
):
    _ensure_registration_owner(db, user, malop, mamh, lan)
    return db_dangkythi.delete(db, malop, mamh, lan)


@router.get("/monhocdk", response_model=List[MonHocDisplay])
def get_monhoc_dangky(
    magv: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
):
    if user.get("role") == "GIANGVIEN":
        magv = user.get("ma")
    return db_dangkythi.get_monhocdk(db, magv)

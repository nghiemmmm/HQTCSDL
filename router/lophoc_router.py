from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from schemas.schemas import LopDisplay, SinhVienWithLopDisplay
from db.database import get_db
from db import db_lop, db_sinhvien

router = APIRouter(
    prefix="/lop",
    tags=["Lop"]
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def hien_thi_sinh_vien(request: Request):
    return templates.TemplateResponse("formSinhVien.html", {"request": request})


@router.get("/lophoc", response_model=List[LopDisplay])
def get_all_lophoc(db: Session = Depends(get_db)):
    return db_lop.get_all_lop(db)


@router.post("/", response_model=LopDisplay)
def them_lop_moi(lop: LopDisplay, db: Session = Depends(get_db)):
	"""
	Thêm lớp mới
	"""
	return db_lop.them_lop(db, lop)


@router.put("/{malop}", response_model=LopDisplay)
def sua_lop_existing(malop: str, lop: LopDisplay, db: Session = Depends(get_db)):
	"""
	Sửa thông tin lớp
	"""
	return db_lop.sua_lop(db, malop, lop)


@router.delete("/{malop}")
def xoa_lop_existing(malop: str, db: Session = Depends(get_db)):
	"""
	Xóa lớp
	"""
	db_lop.xoa_lop(db, malop)
	return {"message": f"Xóa lớp {malop} thành công"}


@router.get("/{malop}", response_model=List[SinhVienWithLopDisplay])
def get_sinh_vien_by_lop(malop: str, db: Session = Depends(get_db)):
	return db_sinhvien.lay_ds_sinh_vien_mot_lop(db, malop)
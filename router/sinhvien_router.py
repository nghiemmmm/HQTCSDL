from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from schemas.schemas import SinhVienDisplay, SinhVienBase, SinhVienWithLopDisplay
from db.database import get_db
from db import db_lop, db_monhoc, db_sinhvien

router = APIRouter(
    prefix="/sinhvien",
    tags=["Sinhvien"]
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def hienThiMonHoc(request: Request):
    return templates.TemplateResponse("formSinhVien.html", {"request": request})


@router.get("/lop/{malop}", response_model=List[SinhVienWithLopDisplay])
def get_sinh_vien_by_lop(malop: str, db: Session = Depends(get_db)):
    return db_sinhvien.lay_ds_sinh_vien_mot_lop(db, malop=malop)


@router.post("/", response_model=SinhVienDisplay)
def create_sinh_vien(sinhvien: SinhVienBase, db: Session = Depends(get_db)):
	"""
	Thêm sinh viên mới
	"""
	return db_sinhvien.them_sinhvien(db, sinhvien)


@router.put("/{masv}", response_model=SinhVienDisplay)
def update_sinh_vien(masv: str, sinhvien: SinhVienBase, db: Session = Depends(get_db)):
	"""
	Cập nhật thông tin sinh viên
	"""
	return db_sinhvien.sua_sinhvien(db, masv, sinhvien)


@router.delete("/{masv}")
def delete_sinh_vien(masv: str, db: Session = Depends(get_db)):
	"""
	Xóa sinh viên
	"""
	db_sinhvien.xoa_sinhvien(db, masv)
	return {"message": f"Xóa sinh viên {masv} thành công"}
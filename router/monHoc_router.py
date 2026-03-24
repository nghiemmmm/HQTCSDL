from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from schemas.schemas import  UserBase, UserDisplay,DangNhapBase,SinhVienBase,DangKyBase,MonHocDisplay,MonHocBase
from db.database import get_db
from db import db_monhoc

router = APIRouter(
    prefix="/monhoc",
    tags=["MonHoc"]
)


@router.post("/")
def create_monhoc(request: MonHocBase, db: Session = Depends(get_db)):
    return db_monhoc.taoMonHoc(db, request)


@router.get("/")
def get_all_monhoc(db: Session = Depends(get_db)):
    return db_monhoc.getAllMonHoc(db)


@router.get("/{mamh}")
def get_monhoc(mamh: str, db: Session = Depends(get_db)):
    return db_monhoc.getMonHocById(mamh, db)


@router.put("/{mamh}")
def update_monhoc(mamh: str, request: MonHocBase, db: Session = Depends(get_db)):
    return db_monhoc.updateMonHoc(mamh, request, db)


@router.delete("/{mamh}")
def delete_monhoc(mamh: str, db: Session = Depends(get_db)):
    return db_monhoc.deleteMonHoc(mamh, db)
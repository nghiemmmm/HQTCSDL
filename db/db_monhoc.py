from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status
from sqlalchemy import exc, or_
from schemas.schemas import MonHocBase
from db.model import DbMonHoc, DbGiaoVienDangKy


def get_all(db: Session):
    try:
        return db.query(DbMonHoc).all()
    except exc.SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Xay ra loi khi truy van danh sach mon hoc: {str(e)}"},
        )

def get_by_id(db: Session, mamh: str):
    monhoc = db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh).first()
    if not monhoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Khong tim thay mon hoc co ma: {mamh}"},
        )
    return monhoc



def create(db: Session, request: MonHocBase):
    duplicate = check_duplicate_monhoc(db, request.mamh, request.tenmh)

    if duplicate["duplicate_mamh"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": f"Ma mon hoc da ton tai: {request.mamh}"},
        )

    if duplicate["duplicate_tenmh"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": f"Ten mon hoc da ton tai: {request.tenmh}"},
        )

    new_mh = DbMonHoc(mamh=request.mamh, tenmh=request.tenmh)
    try:
        db.add(new_mh)
        db.commit()
        db.refresh(new_mh)
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Them mon hoc that bai: {str(e)}"},
        )
    return new_mh

def update(db: Session, mamh: str, request: MonHocBase):
    monhoc = get_by_id(db, mamh)

    check_result = check_monhoc_da_dk(db, mamh)
    if check_result["da_dangky_thi"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Mon hoc da dang ky thi, khong duoc phep sua"},
        )

    try:
        monhoc.tenmh = request.tenmh
        db.commit()
        db.refresh(monhoc)
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Cap nhat mon hoc that bai: {str(e)}"},
        )

    return monhoc

def delete(db: Session, mamh: str):
    monhoc = get_by_id(db, mamh)

    check_result = check_monhoc_da_dk(db, mamh)
    if check_result["da_dangky_thi"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Mon hoc da dang ky thi, khong duoc phep xoa"},
        )

    try:
        db.delete(monhoc)
        db.commit()
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Xoa mon hoc that bai: {str(e)}"},
        )

    return {"message": f"Da xoa mon hoc: {mamh}"}


def search(db: Session, keyword: str):
    kw = (keyword or "").strip()
    if not kw:
        return get_all(db)

    pattern = f"%{kw}%"
    try:
        return (
            db.query(DbMonHoc)
            .filter(or_(DbMonHoc.mamh.ilike(pattern), DbMonHoc.tenmh.ilike(pattern)))
            .all()
        )
    except exc.SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Tim kiem mon hoc that bai: {str(e)}"},
        )

def check_monhoc_da_dk(db: Session, mamh: str):
    ma = (mamh or "").strip()
    if not ma:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Ma mon hoc khong duoc de trong"},
        )

    monhoc = db.query(DbMonHoc).filter(DbMonHoc.mamh == ma).first()
    if not monhoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Khong tim thay mon hoc co ma: {ma}"},
        )

    try:
        da_dang_ky = (
            db.query(DbGiaoVienDangKy)
            .filter(DbGiaoVienDangKy.mamh == ma)
            .first()
            is not None
        )
        return {
            "mamh": ma,
            "da_dangky_thi": da_dang_ky,
            "thong_bao": (
                "Mon hoc da duoc dang ky thi"
                if da_dang_ky
                else "Mon hoc chua duoc dang ky thi"
            ),
        }
    except exc.SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Kiem tra mon hoc dang ky thi that bai: {str(e)}"},
        )
def check_duplicate_monhoc(db: Session, mamh: str, tenmh: str, exclude_mamh: str = None):
    ma_query = db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh)
    ten_query = db.query(DbMonHoc).filter(DbMonHoc.tenmh == tenmh)

    if exclude_mamh:
        ma_query = ma_query.filter(DbMonHoc.mamh != exclude_mamh)
        ten_query = ten_query.filter(DbMonHoc.mamh != exclude_mamh)

    existed_ma = ma_query.first() is not None
    existed_ten = ten_query.first() is not None

    return {
        "duplicate_mamh": existed_ma,
        "duplicate_tenmh": existed_ten,
    }

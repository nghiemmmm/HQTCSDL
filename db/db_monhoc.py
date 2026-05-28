from sqlalchemy.orm import Session
from sqlalchemy import exc, or_
from fastapi import HTTPException, status

from db.model import DbMonHoc, DbGiaoVienDangKy
from schemas.schemas import MonHocBase,MonHocDisplay

# ======================
# GET ALL
# ======================
def get_all(db: Session):
    try:
        mon_hocs = db.query(DbMonHoc).all()
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu khi truy xuất môn học: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống không xác định: {str(e)}"
        )
    return mon_hocs


# ======================
# GET BY ID
# ======================
def get_by_id(db: Session, mamh: str):
    monhoc = db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh).first()
    if not monhoc:
        raise HTTPException(404, "Không tìm thấy môn học")
    return monhoc


# ======================
# CREATE
# ======================
def create(db: Session, request: MonHocBase):
    dup = check_duplicate_monhoc(db, request.mamh, request.tenmh)

    if dup["duplicate_mamh"]:
        raise HTTPException(400, "Mã môn học đã tồn tại")

    if dup["duplicate_tenmh"]:
        raise HTTPException(400, "Tên môn học đã tồn tại")

    obj = DbMonHoc(**request.dict())

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {
            "message": f"Thêm thành công môn học: {obj.tenmh}",
            "data": {"mamh": obj.mamh, "tenmh": obj.tenmh}
        }
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, str(e))


# ======================
# UPDATE
# ======================
def update(db: Session, mamh: str, request: MonHocBase):
    obj = get_by_id(db, mamh)

    if check_monhoc_da_dk(db, mamh)["da_dangky_thi"]:
        raise HTTPException(400, "Đã đăng ký thi không được sửa")

    try:
        obj.tenmh = request.tenmh
        db.commit()
        db.refresh(obj)
        return {
            "message": f"Sửa thành công môn học: {obj.tenmh}",
            "data": {"mamh": obj.mamh, "tenmh": obj.tenmh}
        }
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, str(e))


# ======================
# DELETE
# ======================
def delete(db: Session, mamh: str):
    obj = get_by_id(db, mamh)

    if check_monhoc_da_dk(db, mamh)["da_dangky_thi"]:
        raise HTTPException(400, "Đã đăng ký thi không được xóa")

    try:
        db.delete(obj)
        db.commit()
        return {"message": f"Xóa thành công môn học: {obj.tenmh}"}
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, str(e))


# ======================
# SEARCH
# ======================
def search(db: Session, keyword: str):
    if not keyword:
        return get_all(db)

    return db.query(DbMonHoc).filter(
        or_(
            DbMonHoc.mamh.ilike(f"%{keyword}%"),
            DbMonHoc.tenmh.ilike(f"%{keyword}%")
        )
    ).all()


# ======================
# CHECK REGISTER
# ======================
def check_monhoc_da_dk(db: Session, mamh: str):
    exists = db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.mamh == mamh
    ).first() is not None

    return {
        "mamh": mamh,
        "da_dangky_thi": exists
    }


# ======================
# CHECK DUPLICATE
# ======================
def check_duplicate_monhoc(db: Session, mamh: str, tenmh: str):
    return {
        "duplicate_mamh": db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh).first() is not None,
        "duplicate_tenmh": db.query(DbMonHoc).filter(DbMonHoc.tenmh == tenmh).first() is not None,
    }
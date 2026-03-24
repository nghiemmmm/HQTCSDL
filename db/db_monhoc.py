from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from db.database import engine
from schemas.schemas import DangNhapBase,SinhVienBase,MonHocBase
from db.model import MonHoc
from sqlalchemy import exc
from db.model import DbMonHoc


def taoMonHoc(db: Session, request: MonHocBase):
    '''
    Tao mon hoc moi vao CSDL 
    cac thong tin yeu cau dung cung cap nhu khai bao DbMonHoc
    200:
    _ new_mh : thong tin mon hoc da duoc tao 
    500:
    - `"message":f"them du lieu moi khong thanh :{e}"`
    '''
    new_mh = DbMonHoc(
        mamh = request.mamh,
        tenmh = request.tenmh
    )
    try:
        db.add(new_mh)
        db.commit()
        db.refresh(new_mh)
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message":f"them du lieu moi khong thanh"
            }
        )
    return new_mh


def getAllMonHoc(db: Session):
    '''
    truy van tat ca các mon hoc trong bang MONHOC 
    200:  
    - `monhoc`: Danh sách tất cả mon hoc   
    500:  
    - `"message": f"Xảy ra lỗi trong quá trình truy vấn thông tin mon hoc: {e}"`
    '''
    try:
        monhoc = db.query(DbMonHoc).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER,
            detail={
                'message': f"Xảy ra lỗi trong quá trình truy vấn thông tin mon hoc: {e}"
            }
        )
    return monhoc

def getMonHocById(db: Session,mamh: str):
    '''
    truy van mon hoc co ma mamh = mamh trong bang MONHOC 
    404:  
    - `monhoc`: khong tim thay mon hoc co mamh = mamh  
    '''
    monhoc = db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh).first()
    if not monhoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy môn học có mã môn học: {mamh}"
            }
        )
    return monhoc

def updateMonHoc(mamh: str, request: MonHocBase, db: Session):

    monhoc = db.query(DbMonHoc).filter(DbMonHoc.mamh == mamh)

    if not monhoc.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học để cập nhật"
        )

    try:
        monhoc.update({
            MonHoc.tenmh: request.tenmh
        })

        db.commit()

    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cập nhật thất bại: {str(e)}"
        )

    return {"message": "Cập nhật môn học thành công"}

def deleteMonHoc(db: Session,mamh: str, current_admin: str):
    """
    Xóa thông tin một MonHoc dựa vào mã MonHoc `(MAMH)`  
    Việc xóa thông tin MonHoc chỉ được phép thức thi với một số người nhất định, gọi là `admin`.  
    Kết quả trả về:  
    200:  
    - `"message": f"{current_admin} Đã xóa thành công MonHoc: {MAMH}"`  
    404:   
    - `"message": f"{current_admin}: Không tìm thấy MonHoc có mã MonHoc: {MAMH}"`  
    500:  
    - `"message": f"Có lỗi trong quá trình xóa MonHoc {MAHH}: {e}"`
    """
    monhoc = db.query(MonHoc).filter(MonHoc.mamh == mamh).first()

    if not monhoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"{current_admin}: Không tìm thấy môn học có mã môn học: {mamh}"
            }
        )

    try:
        db.delete()
        db.commit()

    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"co loi trong qua trinh xoa mon hoc {mamh}: {str(e)}"
        )

    return {"message": f"{current_admin} da xoa môn học thành công : {mamh}"}
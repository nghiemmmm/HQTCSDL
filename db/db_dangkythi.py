from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session
from db.model import DbGiaoVienDangKy, DbMonHoc, DbLop, DbGiaoVien
from schemas.schemas import DangKyThi

def create(db: Session, request: DangKyThi):
    # Check if MonHoc exists
    monhoc = db.query(DbMonHoc).filter(DbMonHoc.mamh == request.mamh).first()
    if not monhoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Môn học với mã {request.mamh} không tồn tại")

    # Check if Lop exists
    lop = db.query(DbLop).filter(DbLop.malop == request.malop).first()
    if not lop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lớp với mã {request.malop} không tồn tại")

    # Check if GiaoVien exists (if magv is provided)
    if request.magv:
        giaovien = db.query(DbGiaoVien).filter(DbGiaoVien.magv == request.magv).first()
        if not giaovien:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Giáo viên với mã {request.magv} không tồn tại")

    # Check if the registration already exists (Primary Key: malop, mamh, lan)
    existing_reg = db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.mamh == request.mamh,
        DbGiaoVienDangKy.malop == request.malop,
        DbGiaoVienDangKy.lan == request.lan
    ).first()
    
    if existing_reg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Lịch thi cho lớp {request.malop}, môn {request.mamh} lần {request.lan} đã được đăng ký."
        )

    # Call Stored Procedure to check if there are enough questions in BODE
    from sqlalchemy import text
    try:
        sp_result = db.execute(
            text("EXEC SP_KiemTraSoLuongCauHoi @MAMH=:mamh, @TRINHDO=:trinhdo, @SOCAUTHI=:socauthi"),
            {"mamh": request.mamh, "trinhdo": request.trinhdo, "socauthi": request.socauthi}
        ).fetchone()

        if sp_result and sp_result[0] == 0: # IsHopLe is the first column
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=sp_result[2] # ThongBao is the third column
            )
    except Exception as e:
        # Fallback to ORM check if SP is not yet created in the database
        # (Useful for development before running the SQL script)
        from db.model import DbBoDe
        so_cau_co_san = db.query(DbBoDe).filter(
            DbBoDe.mamh == request.mamh, 
            DbBoDe.trinhdo == request.trinhdo
        ).count()
        if so_cau_co_san < request.socauthi:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không đủ câu hỏi. Yêu cầu: {request.socauthi}, Hiện có: {so_cau_co_san}"
            )

    new_reg = DbGiaoVienDangKy(
        magv=request.magv,
        mamh=request.mamh,
        malop=request.malop,
        trinhdo=request.trinhdo,
        ngaythi=request.ngaythi,
        lan=request.lan,
        socauthi=request.socauthi,
        thoigian=request.thoigian
    )
    
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg

def get_all(db: Session):
    return db.query(DbGiaoVienDangKy).all()

def get_by_lop(db: Session, malop: str):
    return db.query(DbGiaoVienDangKy).filter(DbGiaoVienDangKy.malop == malop).all()

def delete(db: Session, malop: str, mamh: str, lan: int):
    reg = db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.malop == malop,
        DbGiaoVienDangKy.mamh == mamh,
        DbGiaoVienDangKy.lan == lan
    ).first()
    
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lịch đăng ký thi")
        
    db.delete(reg)
    db.commit()
    return {"message": "Xóa lịch thi thành công"}
    
def get_monhocdk(db: Session, magv: str):
    try:
        return db.query(DbMonHoc).join(
            DbGiaoVienDangKy, DbMonHoc.mamh == DbGiaoVienDangKy.mamh
        ).filter(DbGiaoVienDangKy.magv == magv).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi khi lấy môn học đăng ký: {str(e)}"
        )
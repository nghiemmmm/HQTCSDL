from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.model import DbBoDe, DbPhienThi
from schemas.schemas import CauHoiCreate, CauHoiUpdate
import json

def get_all_bode(db: Session):
    return db.query(DbBoDe).all()

def create_bode(db: Session, request: CauHoiCreate):
    new_bode = DbBoDe(
        mamh=request.mamh,
        trinhdo=request.trinhdo,
        noidung=request.noidung,
        a=request.a,
        b=request.b,
        c=request.c,
        d=request.d,
        dap_an=request.dap_an,
        magv=request.magv
    )
    db.add(new_bode)
    try:
        db.commit()
        db.refresh(new_bode)
        return new_bode
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def update_bode(db: Session, cauhoi_id: int, request: CauHoiUpdate):
    bode = db.query(DbBoDe).filter(DbBoDe.cauhoi == cauhoi_id).first()
    if not bode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy câu hỏi với id {cauhoi_id}")
    
    bode.mamh = request.mamh
    bode.trinhdo = request.trinhdo
    bode.noidung = request.noidung
    bode.a = request.a
    bode.b = request.b
    bode.c = request.c
    bode.d = request.d
    bode.dap_an = request.dap_an
    bode.magv = request.magv

    try:
        db.commit()
        db.refresh(bode)
        return bode
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def delete_bode(db: Session, cauhoi_id: int):
    bode = db.query(DbBoDe).filter(DbBoDe.cauhoi == cauhoi_id).first()
    if not bode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy câu hỏi với id {cauhoi_id}")
    
    try:
        db.delete(bode)
        db.commit()
        return {"message": "Xóa câu hỏi thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def check_cauhoi_da_su_dung(db: Session, cauhoi_id: int):
    """
    Kiểm tra xem câu hỏi có được sử dụng trong bất kỳ phiên thi nào không
    Returns: {cauhoi: int, da_su_dung: bool, co_the_xoa: bool}
    """
    # Lấy tất cả phiên thi
    phien_this = db.query(DbPhienThi).all()
    
    da_su_dung = False
    for phien_thi in phien_this:
        try:
            # Parse danh sách câu hỏi từ JSON
            danhsach = json.loads(phien_thi.danhsach_cauhoi)
            # Kiểm tra xem câu hỏi có trong danh sách không
            if isinstance(danhsach, list) and cauhoi_id in danhsach:
                da_su_dung = True
                break
        except (json.JSONDecodeError, TypeError):
            continue
    
    return {
        "cauhoi": cauhoi_id,
        "da_su_dung": da_su_dung,
        "co_the_xoa": not da_su_dung,
        "co_the_sua": not da_su_dung
    }

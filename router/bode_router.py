from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_bode, db_giaovien
from db.model import DbBoDe
from db.roles import Permission
from schemas.schemas import CauHoiCreate, CauHoiUpdate, BoDeDisplay
from core.auth import require_permission

router = APIRouter(
    prefix="/bode",
    tags=["bode"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def get_bode_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_QUESTION)),
):
    # Lấy danh sách câu hỏi để truyền vào giao diện
    bodes = db_bode.get_all_bode(db)
    
    # Format dữ liệu theo BoDeDisplay schema
    bodes_data = [BoDeDisplay.model_validate(b).model_dump() for b in bodes]
    
    # Lấy danh sách giáo viên
    giaoviens = db_giaovien.get_all(db)
    giaoviens_data = [{"magv": gv.magv.strip(), "hoten": f"{gv.ho.strip() if gv.ho else ''} {gv.ten.strip() if gv.ten else ''}".strip()} for gv in giaoviens]
    
    return templates.TemplateResponse("formBoDe.html", {
        "request": request,
        "bodes": bodes_data,
        "giaoviens": giaoviens_data
    })

@router.post("/", response_model=BoDeDisplay)
def create_bode(
    request: CauHoiCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.CREATE_QUESTION)),
):
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma")

    new_bode = db_bode.create_bode(db, request)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Thêm câu hỏi thành công!",
            "data": BoDeDisplay.model_validate(new_bode).model_dump()
        }
    )

@router.put("/{id}", response_model=BoDeDisplay)
def update_bode(
    id: int,
    request: CauHoiUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.UPDATE_QUESTION)),
):
    bode = db.query(DbBoDe).filter(DbBoDe.cauhoi == id).first()
    if not bode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Khong tim thay cau hoi voi id {id}")

    if user.get("role") == "GIANGVIEN" and (bode.magv or "").strip() != (user.get("ma") or "").strip():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Khong duoc sua cau hoi cua giao vien khac")

    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma")

    updated_bode = db_bode.update_bode(db, id, request)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Cập nhật câu hỏi thành công!",
            "data": BoDeDisplay.model_validate(updated_bode).model_dump()
        }
    )

@router.delete("/{id}")
def delete_bode(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.DELETE_QUESTION)),
):
    bode = db.query(DbBoDe).filter(DbBoDe.cauhoi == id).first()
    if not bode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Khong tim thay cau hoi voi id {id}")

    if user.get("role") == "GIANGVIEN" and (bode.magv or "").strip() != (user.get("ma") or "").strip():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Khong duoc xoa cau hoi cua giao vien khac")

    result = db_bode.delete_bode(db, id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result
    )
# # bode_router.py
# @router.post("/cauhoi")
# def tao_cauhoi(
#     request: CauHoiCreate,
#     user = Depends(require_permission(Permission.CREATE_QUESTION.value)),
#     db: Session = Depends(get_db)
# ):
#     # Giáo viên chỉ được tạo câu hỏi cho mình
#     if user.get("role") == "GIANGVIEN":
#         request.magv = user.get("magv")
#     return db_bode.tao_cauhoi(db=db, request=request)

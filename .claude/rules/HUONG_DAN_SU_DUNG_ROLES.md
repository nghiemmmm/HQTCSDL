# Hướng Dẫn Sử Dụng Roles và Permissions

## Tổng Quan

Hệ thống có 3 nhóm quyền chính:
- **PGV** (Phó Giám Viên): Toàn quyền quản trị
- **GIANGVIEN** (Giảng Viên): Quyền hạn chế, quản lý câu hỏi và xem điểm
- **SINHVIEN** (Sinh Viên): Chỉ được thi và xem bài thi

---

## 1. Cách Sử Dụng trong Dependencies (Middleware)

### Cập nhật `dependencies/auth.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db.roles import Quyen, Permission, has_permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Lấy thông tin người dùng hiện tại từ JWT token"""
    try:
        payload = decode_jwt(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def require_role(*allowed_roles: str):
    """
    Decorator kiểm tra role của người dùng
    
    Ví dụ:
        @router.get("/admin-only")
        def admin_endpoint(user = Depends(require_role(Quyen.PGV))):
            ...
    """
    def checker(user = Depends(get_current_user)):
        user_role = user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' không có quyền truy cập"
            )
        return user
    return checker

def require_permission(required_permission: str):
    """
    Decorator kiểm tra quyền cụ thể của người dùng
    
    Ví dụ:
        @router.post("/cauhoi")
        def create_question(
            request: CauHoiCreate,
            user = Depends(require_permission(Permission.CREATE_QUESTION)),
            db: Session = Depends(get_db)
        ):
            ...
    """
    def checker(user = Depends(get_current_user)):
        user_role = user.get("role")
        
        if not has_permission(user_role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền: {required_permission}"
            )
        return user
    return checker
```

---

## 2. Cách Sử Dụng trong Các Router

### Ví dụ 1: Router Quản Lý Câu Hỏi (bode_router.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from db.database import get_db
from db.roles import Permission, Quyen
from dependencies.auth import require_permission, require_role
from db import db_bode
from schemas.schemas import CauHoiCreate, CauHoiUpdate

router = APIRouter(prefix="/cauhoi", tags=["Câu Hỏi"])

@router.post("/", response_model=CauHoiDisplay)
def tao_cauhoi(
    request: CauHoiCreate,
    user = Depends(require_permission(Permission.CREATE_QUESTION)),
    db: Session = Depends(get_db)
):
    """
    Tạo câu hỏi thi
    
    Quyền yêu cầu: CREATE_QUESTION
    Nhóm có quyền: PGV, GIANGVIEN
    """
    # Giáo viên chỉ được tạo câu hỏi cho mình
    if user.get("role") == Quyen.GIANG_VIEN.value:
        request.magv = user.get("magv")
    
    return db_bode.tao_cauhoi(db=db, request=request)

@router.put("/{cauhoi_id}")
def cap_nhat_cauhoi(
    cauhoi_id: int,
    request: CauHoiUpdate,
    user = Depends(require_permission(Permission.UPDATE_QUESTION)),
    db: Session = Depends(get_db)
):
    """
    Cập nhật câu hỏi thi
    
    Quyền yêu cầu: UPDATE_QUESTION
    Nhóm có quyền: PGV, GIANGVIEN (chỉ câu hỏi do mình soạn)
    """
    cauhoi = db.query(DbCauHoi).filter(DbCauHoi.id == cauhoi_id).first()
    
    if not cauhoi:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    
    # Giáo viên chỉ được cập nhật câu hỏi do mình soạn
    if user.get("role") == Quyen.GIANG_VIEN.value:
        if cauhoi.magv != user.get("magv"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chỉ được phép cập nhật câu hỏi do mình soạn"
            )
    
    return db_bode.cap_nhat_cauhoi(db=db, cauhoi_id=cauhoi_id, request=request)

@router.delete("/{cauhoi_id}")
def xoa_cauhoi(
    cauhoi_id: int,
    user = Depends(require_permission(Permission.DELETE_QUESTION)),
    db: Session = Depends(get_db)
):
    """
    Xóa câu hỏi thi
    
    Quyền yêu cầu: DELETE_QUESTION
    Nhóm có quyền: PGV
    """
    return db_bode.xoa_cauhoi(db=db, cauhoi_id=cauhoi_id)

@router.get("/{cauhoi_id}")
def xem_cauhoi(
    cauhoi_id: int,
    user = Depends(require_permission(Permission.VIEW_QUESTION)),
    db: Session = Depends(get_db)
):
    """
    Xem câu hỏi thi
    
    Quyền yêu cầu: VIEW_QUESTION
    Nhóm có quyền: PGV, GIANGVIEN
    """
    cauhoi = db.query(DbCauHoi).filter(DbCauHoi.id == cauhoi_id).first()
    
    if not cauhoi:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi")
    
    return cauhoi
```

### Ví dụ 2: Router Thi (thi_router.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from db.database import get_db
from db.roles import Permission, Quyen
from dependencies.auth import require_permission, require_role
from schemas.schemas import BaiThiCreate, BaiThiDisplay

router = APIRouter(prefix="/thi", tags=["Thi"])

@router.post("/lam-thi")
def lam_thi_chinh_thuc(
    request: BaiThiCreate,
    user = Depends(require_permission(Permission.TAKE_EXAM)),
    db: Session = Depends(get_db)
):
    """
    Làm bài thi chính thức (ghi điểm)
    
    Quyền yêu cầu: TAKE_EXAM
    Nhóm có quyền: SINHVIEN
    """
    if user.get("role") != Quyen.SINH_VIEN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ sinh viên mới được làm bài thi chính thức"
        )
    
    request.masv = user.get("masv")
    return db_thi.lam_thi(db=db, request=request, is_scored=True)

@router.post("/thi-thu")
def thi_thu(
    request: BaiThiCreate,
    user = Depends(require_permission(Permission.PRACTICE_EXAM)),
    db: Session = Depends(get_db)
):
    """
    Thi thử (không ghi điểm)
    
    Quyền yêu cầu: PRACTICE_EXAM
    Nhóm có quyền: PGV, GIANGVIEN, SINHVIEN
    """
    request.masv = user.get("masv")
    return db_thi.lam_thi(db=db, request=request, is_scored=False)

@router.get("/xem-lai-thi")
def xem_lai_thi(
    user = Depends(require_permission(Permission.VIEW_OWN_EXAM)),
    db: Session = Depends(get_db)
):
    """
    Xem lại bài thi đã thi (của sinh viên)
    
    Quyền yêu cầu: VIEW_OWN_EXAM
    Nhóm có quyền: SINHVIEN
    """
    masv = user.get("masv")
    exams = db.query(DbBaiThi).filter(DbBaiThi.masv == masv).all()
    return exams
```

### Ví dụ 3: Router Quản Lý Người Dùng (user_router.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from db.database import get_db
from db.roles import Permission, Quyen
from dependencies.auth import require_permission, require_role
from schemas.schemas import UserCreate, UserDisplay

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/register")
def dang_ky(
    request: UserCreate,
    user = Depends(require_permission(Permission.MANAGE_USERS)),
    db: Session = Depends(get_db)
):
    """
    Tạo tài khoản mới
    
    Quyền yêu cầu: MANAGE_USERS
    Nhóm có quyền: PGV
    
    PGV được tạo tài khoản cho:
    - PGV
    - GIANGVIEN
    - SINHVIEN (tài khoản chung)
    """
    if user.get("role") != Quyen.PGV.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ PGV mới được tạo tài khoản"
        )
    
    # Kiểm tra role được tạo có hợp lệ không
    if request.role not in [Quyen.PGV.value, Quyen.GIANG_VIEN.value, Quyen.SINH_VIEN.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role không hợp lệ"
        )
    
    # PGC (Phó Giám Viên Chế độ) không có chức năng thi
    if request.role == "PGC":
        # Gán quyền không bao gồm TAKE_EXAM
        pass
    
    return db_user.dang_ky(db=db, request=request)

@router.delete("/{user_id}")
def xoa_user(
    user_id: int,
    user = Depends(require_permission(Permission.MANAGE_USERS)),
    db: Session = Depends(get_db)
):
    """
    Xóa tài khoản người dùng
    
    Quyền yêu cầu: MANAGE_USERS
    Nhóm có quyền: PGV
    """
    return db_user.xoa_user(db=db, user_id=user_id)
```

### Ví dụ 4: Router Điểm (diem_router.py - nếu có)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from db.database import get_db
from db.roles import Permission, Quyen
from dependencies.auth import require_permission

router = APIRouter(prefix="/diem", tags=["Điểm"])

@router.get("/mon-hoc/{mamh}")
def xem_bang_diem(
    mamh: str,
    user = Depends(require_permission(Permission.VIEW_SCORE_REPORT)),
    db: Session = Depends(get_db)
):
    """
    Xem bảng điểm môn học
    
    Quyền yêu cầu: VIEW_SCORE_REPORT
    Nhóm có quyền: PGV, GIANGVIEN
    """
    return db_diem.lay_bang_diem(db=db, mamh=mamh)

@router.get("/in-bang-diem/{mamh}")
def in_bang_diem(
    mamh: str,
    user = Depends(require_permission(Permission.PRINT_SCORE_TABLE)),
    db: Session = Depends(get_db)
):
    """
    In bảng điểm môn học
    
    Quyền yêu cầu: PRINT_SCORE_TABLE
    Nhóm có quyền: PGV, GIANGVIEN
    """
    return db_diem.in_bang_diem(db=db, mamh=mamh)

@router.get("/sinh-vien/{masv}")
def xem_diem_sinh_vien(
    masv: str,
    user = Depends(require_permission(Permission.VIEW_STUDENT_SCORE)),
    db: Session = Depends(get_db)
):
    """
    Xem điểm của sinh viên (từ giáo viên hoặc PGV)
    
    Quyền yêu cầu: VIEW_STUDENT_SCORE
    Nhóm có quyền: PGV, GIANGVIEN
    """
    return db_diem.lay_diem_sinh_vien(db=db, masv=masv)
```

---

## 3. Bảng Tóm Tắt Quyền

| Quyền | PGV | GIANGVIEN | SINHVIEN |
|-------|-----|-----------|----------|
| **Quản Lý Người Dùng** | ✅ | ❌ | ❌ |
| Tạo Tài Khoản | ✅ | ❌ | ❌ |
| Xóa Tài Khoản | ✅ | ❌ | ❌ |
| **Câu Hỏi Thi** | ✅ | ✅* | ❌ |
| Tạo Câu Hỏi | ✅ | ✅ | ❌ |
| Cập Nhật Câu Hỏi | ✅ | ✅* | ❌ |
| Xóa Câu Hỏi | ✅ | ❌ | ❌ |
| **Bộ Đề Thi** | ✅ | ❌ | ❌ |
| **Thi** | ✅ | ⚠️ | ✅ |
| Thi Chính Thức | ❌ | ❌ | ✅ |
| Thi Thử | ✅ | ✅ | ✅ |
| **Điểm** | ✅ | ✅ | ⚠️ |
| Xem Bảng Điểm | ✅ | ✅ | ❌ |
| In Bảng Điểm | ✅ | ✅ | ❌ |
| **Xem Bài Thi** | ✅ | ✅ | ⚠️ |
| Xem Bài Thi Sinh Viên | ✅ | ✅ | ❌ |

**Ghi chú:**
- `✅` = Có quyền
- `❌` = Không có quyền
- `⚠️` = Có quyền nhưng hạn chế (chỉ xem của mình)
- `*` = Chỉ được quản lý câu hỏi do mình soạn

---

## 4. Lưu Ý Quan Trọng

1. **Kiểm tra Role + Business Logic**: 
   - Kiểm tra role giúp xác định quyền chung
   - Kiểm tra business logic giúp xác định quyền chi tiết (ví dụ: giáo viên chỉ xem câu hỏi do mình soạn)

2. **JWT Token**:
   - Token phải chứa `role` và các thông tin cần thiết (`magv`, `masv`, v.v.)
   - Decode token trong `get_current_user()`

3. **Thứ Tự Kiểm Tra**:
   - Kiểm tra role trước (nhanh hơn)
   - Kiểm tra permission sau (chi tiết hơn)
   - Kiểm tra business logic cuối cùng

4. **Error Handling**:
   - 401 Unauthorized: Token không hợp lệ
   - 403 Forbidden: Không có quyền
   - 404 Not Found: Tài nguyên không tồn tại

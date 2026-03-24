from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, List
from schemas.roles import UserRoleEnum, SystemRoleEnum




# --- MON HOC SCHEMAS ---

class DangNhapBase(BaseModel):
    username: str
    password: str
    role: UserRoleEnum  # Role người dùng: SINHVIEN, GIANGVIEN, PGV
    
class DangKyBase(BaseModel):
    hoten: str 
    username: str
    manv: str 
    password: str
    loginname: str 
    system_role: SystemRoleEnum = SystemRoleEnum.user  # Quyền hệ thống: ADMIN, USER (mặc định USER)

class MonHocBase(BaseModel):
    mamh: str = Field(..., max_length=5)
    tenmh: Optional[str] = Field(None, max_length=50)

class MonHocDisplay(MonHocBase):
    model_config = ConfigDict(from_attributes=True)


# --- LOP SCHEMAS ---

class LopBase(BaseModel):
    malop: str = Field(..., max_length=15)
    tenlop: str = Field(..., max_length=50)

class LopDisplay(LopBase):
    model_config = ConfigDict(from_attributes=True)


# --- SINH VIEN SCHEMAS ---

class UserBase(BaseModel):
    ma: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=50)
    ten: Optional[str] = Field(None, max_length=10)
    role: Optional[str] = Field(None, max_length=10)
class SinhVienDisplay(UserBase):
    """Hiển thị thông tin sinh viên kèm tên lớp nếu cần qua join"""
    ten_lop_day_du: Optional[str] = None


# --- GIAO VIEN SCHEMAS ---
class GiaoVienChuaDK(BaseModel):
    magv: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=50)
    ten: Optional[str] = Field(None, max_length=10)
    model_config = ConfigDict(from_attributes=True)


# --- SYSTEM USER SCHEMAS ---
class SystemUserBase(BaseModel):
    """Thông tin người dùng hệ thống"""
    username: str
    user_role: UserRoleEnum  # Role người dùng (SINHVIEN, GIANGVIEN, PGV)
    system_role: SystemRoleEnum  # Role hệ thống (ADMIN, USER)

class SystemUserDisplay(SystemUserBase):
    """Hiển thị thông tin người dùng hệ thống"""
    pass


# --- GIAO VIEN SCHEMAS ---

class GiaoVienBase(BaseModel):
    magv: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=50)
    ten: Optional[str] = Field(None, max_length=10)
    diachi: Optional[str] = Field(None, max_length=50)
    sodtll: Optional[str] = Field(None, max_length=15)

class GiaoVienDisplay(GiaoVienBase):
    model_config = ConfigDict(from_attributes=True)

class GiaoVienChuaDK(BaseModel):
    magv: str
    ho: Optional[str] = None
    ten: Optional[str] = None

# --- BO DE (Cau Hoi) SCHEMAS ---

class BoDeBase(BaseModel):
    cauhoi: int
    mamh: Optional[str] = Field(None, max_length=5)
    trinhdo: Optional[str] = Field(None, pattern="^[ABC]$")
    noidung: Optional[str] = Field(None, max_length=500)
    a: Optional[str] = Field(None, max_length=200)
    b: Optional[str] = Field(None, max_length=200)
    c: Optional[str] = Field(None, max_length=200)
    d: Optional[str] = Field(None, max_length=200)
    dap_an: Optional[str] = Field(None, pattern="^[ABCD]$")
    magv: Optional[str] = Field(None, max_length=8)

class BoDeDisplay(BoDeBase):
    model_config = ConfigDict(from_attributes=True)


# --- BANG DIEM SCHEMAS ---

class BangDiemBase(BaseModel):
    masv: str
    mamh: str
    lan: int = Field(..., ge=1, le=2)
    ngaythi: Optional[date] = None
    diem: Optional[float] = Field(None, ge=0, le=10)

class BangDiemDisplay(BangDiemBase):
    model_config = ConfigDict(from_attributes=True)


# --- GIAO VIEN DANG KY THI SCHEMAS ---

class GiaoVienDangKyBase(BaseModel):
    magv: Optional[str] = Field(None, max_length=8)
    mamh: str
    malop: str
    trinhdo: Optional[str] = Field(None, pattern="^[ABC]$")
    ngaythi: Optional[datetime] = None
    lan: int = Field(..., ge=1, le=2)
    socauthi: Optional[int] = Field(None, ge=10, le=100)
    thoigian: Optional[int] = Field(None, ge=15, le=60)

class GiaoVienDangKyDisplay(GiaoVienDangKyBase):
    model_config = ConfigDict(from_attributes=True)

class ModeBase(BaseModel):
    mode : str

class ModeDisplay(BaseModel):
    mode: str
    time: datetime
    class Config():
        from_attributes  = True
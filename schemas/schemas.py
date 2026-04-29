from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, List
from db.roles import quyen



# thao tac dang ki dang nhap 
class DangNhap(BaseModel):
    username: str
    password: str = "1234"
    role: quyen
    
class DangKy(BaseModel):   
    loginname: str 
    password: str
    username: str
    role: quyen

# --- MON HOC SCHEMAS ---
class MonHocBase(BaseModel):
    mamh: str = Field(..., max_length=5)
    tenmh: str = Field(..., max_length=50)

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


class SinhVienBase(BaseModel):
    masv: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=50)
    ten: Optional[str] = Field(None, max_length=10)
    ngaysinh: Optional[date] = None
    diachi: Optional[str] = Field(None, max_length=100)
    malop: Optional[str] = Field(None, max_length=15)
    password: str = Field(default="123456", max_length=255)


class SinhVienDisplay(BaseModel):
    """Hiển thị thông tin sinh viên: mã SV, họ, tên, ngày sinh"""
    masv: str
    ho: Optional[str] = None
    ten: Optional[str] = None
    ngaysinh: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)


class SinhVienWithLopDisplay(BaseModel):
    """Hiển thị thông tin sinh viên kèm mã lớp"""
    masv: str
    ho: Optional[str] = None
    ten: Optional[str] = None
    ngaysinh: Optional[date] = None
    malop: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- GIAO VIEN SCHEMAS ---
class GiaoVien(BaseModel):
    magv: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=50)
    ten: Optional[str] = Field(None, max_length=10)
    model_config = ConfigDict(from_attributes=True)


# --- SYSTEM USER SCHEMAS ---
class SystemUserBase(BaseModel):
    """Thông tin người dùng hệ thống"""
    username: str
    user_role: quyen # Role người dùng (SINHVIEN, GIANGVIEN, PGV)
    system_role: quyen  # Role hệ thống (ADMIN, USER)

class SystemUserDisplay(SystemUserBase):
    """Hiển thị thông tin người dùng hệ thống"""
    pass


# --- GIAO VIEN SCHEMAS ---

class GiaoVien(BaseModel):
    magv: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=50)
    ten: Optional[str] = Field(None, max_length=10)
    diachi: Optional[str] = Field(None, max_length=50)
    sodtll: Optional[str] = Field(None, max_length=15)

class GiaoVienDisplay(GiaoVien):
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

class GiaoVienDangNhap(BaseModel):
    magv: Optional[str] = Field(None, max_length=8)
    mamh: str
    malop: str
    trinhdo: Optional[str] = Field(None, pattern="^[ABC]$")
    ngaythi: Optional[datetime] = None
    lan: int = Field(..., ge=1, le=2)
    socauthi: Optional[int] = Field(None, ge=10, le=100)
    thoigian: Optional[int] = Field(None, ge=15, le=60)

class GiaoVienDangKyDisplay(GiaoVienDangNhap):
    model_config = ConfigDict(from_attributes=True)

class ModeBase(BaseModel):
    mode : str

class ModeDisplay(BaseModel):
    mode: str
    time: datetime
    class Config():
        from_attributes  = True
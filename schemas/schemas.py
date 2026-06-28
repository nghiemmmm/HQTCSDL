from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from db.roles import quyen


class SystemRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


# --- AUTHENTICATION SCHEMAS ---

class DangNhap(BaseModel):
    username: str
    password: str
    role: quyen


class DangKy(BaseModel):
    loginname: str
    password: str
    username: str
    role: quyen


# --- USER SCHEMAS ---

class UserBase(BaseModel):
    ma: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=40)
    ten: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=50)


class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)


# --- MON HOC SCHEMAS ---

class MonHocBase(BaseModel):
    mamh: str = Field(..., max_length=5)
    tenmh: str = Field(..., max_length=40)


class MonHocCreate(MonHocBase):
    pass


class MonHocUpdate(BaseModel):
    tenmh: Optional[str] = Field(None, max_length=40)


class MonHocPublic(MonHocBase):
    model_config = ConfigDict(from_attributes=True)


# --- LOP SCHEMAS ---

class LopBase(BaseModel):
    malop: str = Field(..., max_length=15)
    tenlop: str = Field(..., max_length=40)


class LopCreate(LopBase):
    pass


class LopUpdate(BaseModel):
    tenlop: Optional[str] = Field(None, max_length=40)


class LopPublic(LopBase):
    model_config = ConfigDict(from_attributes=True)


# --- SINH VIEN SCHEMAS ---

class SinhVienBase(BaseModel):
    masv: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=40)
    ten: Optional[str] = Field(None, max_length=50)
    ngaysinh: Optional[date] = None
    diachi: Optional[str] = Field(None, max_length=100)
    malop: Optional[str] = Field(None, max_length=15)


class SinhVienCreate(SinhVienBase):
    password: str = Field(..., max_length=255)


class SinhVienUpdate(BaseModel):
    ho: Optional[str] = Field(None, max_length=40)
    ten: Optional[str] = Field(None, max_length=50)
    ngaysinh: Optional[date] = None
    diachi: Optional[str] = Field(None, max_length=100)
    malop: Optional[str] = Field(None, max_length=15)
    password: Optional[str] = Field(None, max_length=255)


class SinhVienPublic(BaseModel):
    """Hiển thị thông tin sinh viên: mã SV, họ, tên, ngày sinh"""
    masv: str
    ho: Optional[str] = None
    ten: Optional[str] = None
    ngaysinh: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class SinhVienWithLopPublic(SinhVienPublic):
    """Hiển thị thông tin sinh viên kèm mã lớp"""
    malop: Optional[str] = None


# --- SYSTEM USER SCHEMAS ---

class SystemUserBase(BaseModel):
    """Thông tin người dùng hệ thống"""
    username: str
    user_role: quyen  # Role người dùng (SINHVIEN, GIANGVIEN, PGV)
    system_role: SystemRole  # Role hệ thống (ADMIN, USER)


class SystemUserPublic(SystemUserBase):
    """Hiển thị thông tin người dùng hệ thống"""
    model_config = ConfigDict(from_attributes=True)


# --- GIAO VIEN SCHEMAS ---

class GiaoVienBase(BaseModel):
    magv: str = Field(..., max_length=8)
    ho: Optional[str] = Field(None, max_length=40)
    ten: Optional[str] = Field(None, max_length=50)
    diachi: Optional[str] = Field(None, max_length=50)
    sodtll: Optional[str] = Field(None, max_length=15)


class GiaoVienCreate(GiaoVienBase):
    pass


class GiaoVienUpdate(BaseModel):
    ho: Optional[str] = Field(None, max_length=40)
    ten: Optional[str] = Field(None, max_length=50)
    diachi: Optional[str] = Field(None, max_length=50)
    sodtll: Optional[str] = Field(None, max_length=15)


class GiaoVienPublic(GiaoVienBase):
    model_config = ConfigDict(from_attributes=True)


class GiaoVienChuaDK(BaseModel):
    magv: str
    ho: Optional[str] = None
    ten: Optional[str] = None


# --- BO DE (Cau Hoi) SCHEMAS ---

class BoDeBase(BaseModel):
    mamh: str = Field(..., max_length=5)
    trinhdo: str = Field(..., pattern="^[ABC]$")
    noidung: str = Field(..., max_length=200)
    a: str = Field(..., max_length=200)
    b: str = Field(..., max_length=200)
    c: str = Field(..., max_length=200)
    d: str = Field(..., max_length=200)
    dap_an: str = Field(..., pattern="^[ABCD]$")
    magv: Optional[str] = Field(None, max_length=8)


class CauHoiCreate(BoDeBase):
    pass


class CauHoiUpdate(BaseModel):
    mamh: Optional[str] = Field(None, max_length=5)
    trinhdo: Optional[str] = Field(None, pattern="^[ABC]$")
    noidung: Optional[str] = Field(None, max_length=200)
    a: Optional[str] = Field(None, max_length=200)
    b: Optional[str] = Field(None, max_length=200)
    c: Optional[str] = Field(None, max_length=200)
    d: Optional[str] = Field(None, max_length=200)
    dap_an: Optional[str] = Field(None, pattern="^[ABCD]$")
    magv: Optional[str] = Field(None, max_length=8)


class BoDePublic(BoDeBase):
    cauhoi: int
    model_config = ConfigDict(from_attributes=True)


# --- BANG DIEM SCHEMAS ---

class BangDiemBase(BaseModel):
    masv: str
    mamh: str
    lan: int = Field(..., ge=1, le=2)
    ngaythi: Optional[date] = None
    diem: Optional[float] = Field(None, ge=0, le=10)


class BangDiemCreate(BangDiemBase):
    pass


class BangDiemUpdate(BaseModel):
    lan: Optional[int] = Field(None, ge=1, le=2)
    ngaythi: Optional[date] = None
    diem: Optional[float] = Field(None, ge=0, le=10)


class BangDiemPublic(BangDiemBase):
    model_config = ConfigDict(from_attributes=True)


# --- GIAO VIEN DANG KY THI SCHEMAS ---

class DangKyThi(BaseModel):
    magv: Optional[str] = Field(None, max_length=8)
    mamh: str
    malop: str
    trinhdo: Optional[str] = Field(None, pattern="^[ABC]$")
    ngaythi: Optional[datetime] = None
    lan: int = Field(..., ge=1, le=2)
    socauthi: Optional[int] = Field(None, ge=10, le=100)
    thoigian: Optional[int] = Field(None, ge=5, le=60)


class ThongTinThi(DangKyThi):
    active_session_status: Optional[str] = None
    active_session_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class GiaoVienDangKyThiPublic(DangKyThi):
    model_config = ConfigDict(from_attributes=True)


# --- MODE SCHEMAS ---

class ModeBase(BaseModel):
    mode: str


class ModePublic(ModeBase):
    time: datetime
    model_config = ConfigDict(from_attributes=True)


# --- MESSAGE SCHEMA ---

class Message(BaseModel):
    message: str


# --- EXAM SESSION REQUESTS ---

class BaiNopRequest(BaseModel):
    """Answers submitted for one official exam session."""

    session_id: Optional[int] = None
    mamonhoc: str
    lanthi: int = Field(ge=1, le=2)
    malop: str
    ngaythi: str
    answers: Dict[str, str] = Field(default_factory=dict)


class AutoSaveRequest(BaseModel):
    """Incremental student exam progress."""

    session_id: int
    answers: Dict[str, str] = Field(default_factory=dict)
    current_index: int = 0
    remaining_seconds: int = 0


# --- REPORT AND SEARCH SCHEMAS ---

class StudentShortResponse(BaseModel):
    """Thông tin rút gọn của sinh viên phục vụ dropdown."""
    masv: str
    hoten: str
    model_config = ConfigDict(from_attributes=True)


class TraCuuBaiThiResponse(BaseModel):
    """Kết quả tra cứu bài thi của một sinh viên."""
    session_id: Optional[int] = None
    score: Optional[float] = None
    correct_count: int = 0
    total_count: int = 0
    submitted_at: Optional[str] = None


class BangDiemMonHocPublic(BaseModel):
    """Chi tiết một dòng điểm của sinh viên trong bảng điểm lớp."""
    stt: int
    masv: str
    ho: str
    ten: str
    diem: Union[float, str]  # Điểm số hoặc chữ "Chưa thi"
    diem_chu: str           # Điểm chữ (A, B+, C, ...)
    diem_chu_viet: str      # Điểm chữ viết tiếng Việt (Tám phẩy hai mươi lăm)


class BangDiemMonHocResponse(BaseModel):
    """Bảng điểm môn học của một lớp."""
    students: list[BangDiemMonHocPublic]


# Compatibility aliases keep existing route contracts stable during migration.
MonHocDisplay = MonHocPublic
LopDisplay = LopPublic
SinhVienDisplay = SinhVienPublic
SinhVienWithLopDisplay = SinhVienWithLopPublic
GiaoVien = GiaoVienBase
GiaoVienDisplay = GiaoVienPublic
BoDeDisplay = BoDePublic
BangDiemDisplay = BangDiemPublic
GiaoVienDangKyThiDisplay = GiaoVienDangKyThiPublic
ModeDisplay = ModePublic

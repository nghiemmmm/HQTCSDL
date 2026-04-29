from sqlalchemy import Column, Integer, Float, DateTime, Date, SmallInteger
from sqlalchemy import ForeignKey, CHAR, NCHAR, Unicode, CheckConstraint
from sqlalchemy.orm import relationship
from db.database import Base


class DbMonHoc(Base):
    __tablename__ = "MONHOC"

    mamh = Column(NCHAR(5), primary_key=True)
    tenmh = Column(Unicode(40), unique=True, nullable=False)

    bangdiem = relationship("DbBangDiem", back_populates="monhoc")
    bode = relationship("DbBoDe", back_populates="monhoc")
    giao_vien_dang_ky = relationship("DbGiaoVienDangKy", back_populates="monhoc")


class DbLop(Base):
    __tablename__ = "LOP"

    malop = Column(NCHAR(15), primary_key=True)
    tenlop = Column(Unicode(40), unique=True, nullable=False)

    sinhvien = relationship("DbSinhVien", back_populates="lop")
    giao_vien_dang_ky = relationship("DbGiaoVienDangKy", back_populates="lop")


class DbSinhVien(Base):
    __tablename__ = "SINHVIEN"

    masv = Column(NCHAR(8), primary_key=True)
    ho = Column(Unicode(40))
    ten = Column(Unicode(10))
    ngaysinh = Column(Date)
    diachi = Column(Unicode(100))
    malop = Column(NCHAR(15), ForeignKey("LOP.malop"))
    password = Column(Unicode(255), nullable=False, default="123456")

    lop = relationship("DbLop", back_populates="sinhvien")
    bangdiem = relationship("DbBangDiem", back_populates="sinhvien")


class DbGiaoVien(Base):
    __tablename__ = "GIAOVIEN"

    magv = Column(NCHAR(8), primary_key=True)
    ho = Column(Unicode(40))
    ten = Column(Unicode(10))
    sodtll = Column(NCHAR(15))
    diachi = Column(Unicode(50))

    bode = relationship("DbBoDe", back_populates="giaovien")
    giao_vien_dang_ky = relationship("DbGiaoVienDangKy", back_populates="giaovien")


class DbBoDe(Base):
    __tablename__ = "BODE"

    cauhoi = Column(Integer, primary_key=True, autoincrement=True)
    mamh = Column(NCHAR(5), ForeignKey("MONHOC.mamh"))
    trinhdo = Column(CHAR(1))
    noidung = Column(Unicode(200))
    a = Column(Unicode(50))
    b = Column(Unicode(50))
    c = Column(Unicode(50))
    d = Column(Unicode(50))
    dap_an = Column(CHAR(1))
    magv = Column(NCHAR(8), ForeignKey("GIAOVIEN.magv"))

    __table_args__ = (
        CheckConstraint("trinhdo IN ('A','B','C')"),
        CheckConstraint("dap_an IN ('A','B','C','D')"),
    )

    monhoc = relationship("DbMonHoc", back_populates="bode")
    giaovien = relationship("DbGiaoVien", back_populates="bode")


class DbBangDiem(Base):
    __tablename__ = "BANGDIEM"

    masv = Column(NCHAR(8), ForeignKey("SINHVIEN.masv"), primary_key=True)
    mamh = Column(NCHAR(5), ForeignKey("MONHOC.mamh"), primary_key=True)
    lan = Column(SmallInteger, primary_key=True)
    ngaythi = Column(Date)
    diem = Column(Float)

    __table_args__ = (
        CheckConstraint("lan BETWEEN 1 AND 2"),
        CheckConstraint("diem BETWEEN 0 AND 10"),
    )

    sinhvien = relationship("DbSinhVien", back_populates="bangdiem")
    monhoc = relationship("DbMonHoc", back_populates="bangdiem")


class DbGiaoVienDangKy(Base):
    __tablename__ = "GIAOVIEN_DANGKY"

    malop = Column(NCHAR(15), ForeignKey("LOP.malop"), primary_key=True)
    mamh = Column(NCHAR(5), ForeignKey("MONHOC.mamh"), primary_key=True)
    lan = Column(SmallInteger, primary_key=True)

    magv = Column(NCHAR(8), ForeignKey("GIAOVIEN.magv"))
    trinhdo = Column(CHAR(1))
    ngaythi = Column(DateTime)
    socauthi = Column(SmallInteger)
    thoigian = Column(SmallInteger)

    __table_args__ = (
        CheckConstraint("trinhdo IN ('A','B','C')"),
        CheckConstraint("lan BETWEEN 1 AND 2"),
        CheckConstraint("socauthi BETWEEN 10 AND 100"),
        CheckConstraint("thoigian BETWEEN 15 AND 60"),
    )

    giaovien = relationship("DbGiaoVien", back_populates="giao_vien_dang_ky")
    monhoc = relationship("DbMonHoc", back_populates="giao_vien_dang_ky")
    lop = relationship("DbLop", back_populates="giao_vien_dang_ky")
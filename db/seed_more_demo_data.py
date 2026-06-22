from sqlalchemy import text

from db.database import engine

subjects = [
    ("CSDL", "Co so du lieu", "GV001"),
    ("CTDL", "Cau truc du lieu", "GV001"),
    ("HQT", "He quan tri CSDL", "GV001"),
    ("MMT", "Mang may tinh", "GV002"),
    ("LTHDT", "Lap trinh huong doi tuong", "GV002"),
]
classes = [
    ("D21CQCN03", "Dai hoc CNTT 03"),
    ("D22CQCN01", "Dai hoc CNTT K22 01"),
    ("D22CQCN02", "Dai hoc CNTT K22 02"),
]
students = [
    ("SV004", "Nguyen Hoai", "Nam", "2004-01-11", "TP HCM", "D21CQCN02"),
    ("SV005", "Tran Minh", "Thu", "2004-03-19", "Tay Ninh", "D21CQCN03"),
    ("SV006", "Pham Gia", "Huy", "2004-05-23", "Long An", "D21CQCN03"),
    ("SV007", "Do Quynh", "Anh", "2004-08-14", "Binh Duong", "D22CQCN01"),
    ("SV008", "Bui Thanh", "Lam", "2004-10-05", "Dong Nai", "D22CQCN01"),
    ("SV009", "Vo Ngoc", "Linh", "2004-12-01", "TP HCM", "D22CQCN02"),
]
registrations = [
    ("D21CQCN01", "CTDL", 1, "GV001", "B", 40, 30, 1),
    ("D21CQCN02", "HQT", 1, "GV001", "A", 40, 30, 2),
    ("D22CQCN01", "MMT", 1, "GV002", "B", 40, 30, 1),
    ("D22CQCN02", "LTHDT", 1, "GV002", "C", 40, 30, 3),
]
levels = [("A", "A"), ("B", "B"), ("C", "C")]

with engine.begin() as conn:
    for mamh, tenmh, _ in subjects:
        conn.execute(text("""
            IF NOT EXISTS (SELECT 1 FROM MONHOC WHERE MAMH = :mamh)
            INSERT INTO MONHOC (MAMH, TENMH) VALUES (:mamh, :tenmh)
        """), {"mamh": mamh, "tenmh": tenmh})

    for malop, tenlop in classes:
        conn.execute(text("""
            IF NOT EXISTS (SELECT 1 FROM LOP WHERE MALOP = :malop)
            INSERT INTO LOP (MALOP, TENLOP) VALUES (:malop, :tenlop)
        """), {"malop": malop, "tenlop": tenlop})

    for masv, ho, ten, ngaysinh, diachi, malop in students:
        conn.execute(text("""
            IF NOT EXISTS (SELECT 1 FROM SINHVIEN WHERE MASV = :masv)
            INSERT INTO SINHVIEN (MASV, HO, TEN, NGAYSINH, DIACHI, MALOP, PASSWORD)
            VALUES (:masv, :ho, :ten, :ngaysinh, :diachi, :malop, '123456')
        """), {
            "masv": masv, "ho": ho, "ten": ten, "ngaysinh": ngaysinh,
            "diachi": diachi, "malop": malop,
        })

    for mamh, _, magv in subjects:
        for level, answer in levels:
            for i in range(1, 51):
                conn.execute(text("""
                    IF NOT EXISTS (
                        SELECT 1 FROM BODE
                        WHERE MAMH = :mamh AND TRINHDO = :level AND NOIDUNG = :content
                    )
                    INSERT INTO BODE (MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN, MAGV)
                    VALUES (:mamh, :level, :content, :a, :b, :c, :d, :answer, :magv)
                """), {
                    "mamh": mamh,
                    "level": level,
                    "content": f"{mamh} {level} bo sung cau {i}",
                    "a": f"Lua chon A cau {i}",
                    "b": f"Lua chon B cau {i}",
                    "c": f"Lua chon C cau {i}",
                    "d": f"Lua chon D cau {i}",
                    "answer": answer,
                    "magv": magv,
                })

    for malop, mamh, lan, magv, level, count, duration, day_offset in registrations:
        conn.execute(text("""
            IF NOT EXISTS (
                SELECT 1 FROM GIAOVIEN_DANGKY
                WHERE MALOP = :malop AND MAMH = :mamh AND LAN = :lan
            )
            INSERT INTO GIAOVIEN_DANGKY (MALOP, MAMH, LAN, MAGV, TRINHDO, NGAYTHI, SOCAUTHI, THOIGIAN)
            VALUES (:malop, :mamh, :lan, :magv, :level, DATEADD(DAY, :day_offset, GETDATE()), :count, :duration)
        """), {
            "malop": malop, "mamh": mamh, "lan": lan, "magv": magv,
            "level": level, "count": count, "duration": duration, "day_offset": day_offset,
        })

print("More demo data seeded successfully")

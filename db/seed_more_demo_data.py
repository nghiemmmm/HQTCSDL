from sqlalchemy import text

from db.database import engine

subjects = [
    ("CSDL", "Co so du lieu", "GV001"),
    ("MMT", "Mang may tinh", "GV002"),
    ("CTDL", "Cau truc du lieu", "GV001"),
    ("HQT", "He quan tri CSDL", "GV001"),
    ("LTHDT", "Lap trinh huong doi tuong", "GV002"),
    ("ATTT", "An toan thong tin", "GV003"),
    ("CNPM", "Cong nghe phan mem", "GV004"),
]
classes = [
    ("D21CQCN01", "Dai hoc CNTT 01"),
    ("D21CQCN02", "Dai hoc CNTT 02"),
    ("D21CQCN03", "Dai hoc CNTT 03"),
    ("D22CQCN01", "Dai hoc CNTT K22 01"),
    ("D22CQCN02", "Dai hoc CNTT K22 02"),
    ("D23CQCN01", "Dai hoc CNTT K23 01"),
    ("D23CQCN02", "Dai hoc CNTT K23 02"),
]
teachers = [
    ("PGV001", "Phong", "GiaoVu", "", ""),
    ("GV001", "Nguyen Van", "An", "", ""),
    ("GV002", "Tran Thi", "Binh", "", ""),
    ("GV003", "Le Quoc", "Dat", "", "TP HCM"),
    ("GV004", "Pham Thanh", "Ha", "", "Dong Nai"),
]
students = [
    ("SV004", "Nguyen Hoai", "Nam", "2004-01-11", "TP HCM", "D21CQCN02"),
    ("SV005", "Tran Minh", "Thu", "2004-03-19", "Tay Ninh", "D21CQCN03"),
    ("SV006", "Pham Gia", "Huy", "2004-05-23", "Long An", "D21CQCN03"),
    ("SV007", "Do Quynh", "Anh", "2004-08-14", "Binh Duong", "D22CQCN01"),
    ("SV008", "Bui Thanh", "Lam", "2004-10-05", "Dong Nai", "D22CQCN01"),
    ("SV009", "Vo Ngoc", "Linh", "2004-12-01", "TP HCM", "D22CQCN02"),
    ("SV010", "Nguyen Bao", "Khanh", "2005-01-09", "TP HCM", "D23CQCN01"),
    ("SV011", "Tran My", "Duyen", "2005-04-17", "Lam Dong", "D23CQCN01"),
    ("SV012", "Ho Duc", "Phuc", "2005-06-26", "Binh Phuoc", "D23CQCN01"),
    ("SV013", "Le Thao", "Nhi", "2005-02-12", "Dong Nai", "D23CQCN02"),
    ("SV014", "Pham Minh", "Kiet", "2005-07-30", "Tay Ninh", "D23CQCN02"),
    ("SV015", "Dang Gia", "Bao", "2005-11-03", "TP HCM", "D23CQCN02"),
]
registrations = [
    ("D21CQCN01", "CTDL", 1, "GV001", "B", 40, 30, 1),
    ("D21CQCN02", "HQT", 1, "GV001", "A", 40, 30, 2),
    ("D22CQCN01", "MMT", 1, "GV002", "B", 40, 30, 1),
    ("D22CQCN02", "LTHDT", 1, "GV002", "C", 40, 30, 3),
    ("D23CQCN01", "ATTT", 1, "GV003", "A", 30, 25, 2),
    ("D23CQCN02", "CNPM", 1, "GV004", "B", 30, 25, 2),
    ("D21CQCN03", "HQT", 1, "PGV001", "C", 30, 25, 4),
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

    for magv, ho, ten, sodtll, diachi in teachers:
        conn.execute(text("""
            IF NOT EXISTS (SELECT 1 FROM GIAOVIEN WHERE MAGV = :magv)
            INSERT INTO GIAOVIEN (MAGV, HO, TEN, SODTLL, DIACHI)
            VALUES (:magv, :ho, :ten, :sodtll, :diachi)
        """), {
            "magv": magv, "ho": ho, "ten": ten,
            "sodtll": sodtll, "diachi": diachi,
        })

    for masv, ho, ten, ngaysinh, diachi, malop in students:
        conn.execute(text("""
            IF NOT EXISTS (SELECT 1 FROM SINHVIEN WHERE MASV = :masv)
            INSERT INTO SINHVIEN (MASV, HO, TEN, NGAYSINH, DIACHI, MALOP, PASSWORD)
            VALUES (:masv, :ho, :ten, :ngaysinh, :diachi, :malop, '123456')
        """), {
            "masv": masv, "ho": ho, "ten": ten, "ngaysinh": ngaysinh,
            "diachi": diachi, "malop": malop,
        })

    next_cauhoi = conn.execute(text("SELECT ISNULL(MAX(CAUHOI), 0) FROM BODE")).scalar()

    for mamh, _, magv in subjects:
        for level, answer in levels:
            for i in range(1, 51):
                content = f"{mamh} {level} bo sung cau {i}"
                exists = conn.execute(text("""
                    SELECT 1 FROM BODE
                    WHERE MAMH = :mamh AND TRINHDO = :level AND NOIDUNG = :content
                """), {
                    "mamh": mamh,
                    "level": level,
                    "content": content,
                }).first()
                if exists:
                    continue

                next_cauhoi += 1
                conn.execute(text("""
                    INSERT INTO BODE (CAUHOI, MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN, MAGV)
                    VALUES (:cauhoi, :mamh, :level, :content, :a, :b, :c, :d, :answer, :magv)
                """), {
                    "cauhoi": next_cauhoi,
                    "mamh": mamh,
                    "level": level,
                    "content": content,
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

    conn.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM BANGDIEM WHERE MASV = 'SV010' AND MAMH = 'ATTT' AND LAN = 1)
        BEGIN
            DECLARE @question_json_attt nvarchar(max);
            DECLARE @answer_json_attt nvarchar(max);

            SELECT @question_json_attt = N'[' + STRING_AGG(CONVERT(nvarchar(20), CAUHOI), N',') + N']'
            FROM (
                SELECT TOP (30) CAUHOI
                FROM BODE
                WHERE MAMH = 'ATTT' AND TRINHDO IN ('A', 'B')
                ORDER BY CAUHOI
            ) q;

            SELECT @answer_json_attt = N'{' + STRING_AGG(CONCAT(N'"', CAUHOI, N'":"', DAP_AN, N'"'), N',') + N'}'
            FROM (
                SELECT TOP (30) CAUHOI, DAP_AN
                FROM BODE
                WHERE MAMH = 'ATTT' AND TRINHDO IN ('A', 'B')
                ORDER BY CAUHOI
            ) q;

            INSERT INTO PHIENTHI (
                MASV, MALOP, MAMH, TRINHDO, LAN, SOCAUTHI, THOIGIAN, NGAYTHI,
                BATDAU_LUC, THOIGIAN_CONLAI, TRANGTHAI, DANHSACH_CAUHOI,
                DAPAN_DACHON, CAUHOI_HIENTAI, CAPNHAT_LUC, NOPBAI_LUC, DIEM
            )
            VALUES (
                'SV010', 'D23CQCN01', 'ATTT', 'A', 1, 30, 25, CAST(GETDATE() AS date),
                DATEADD(MINUTE, -20, GETDATE()), 0, N'DA_NOP', @question_json_attt,
                @answer_json_attt, 29, GETDATE(), GETDATE(), 9.5
            );

            INSERT INTO BANGDIEM (MASV, MAMH, LAN, NGAYTHI, DIEM)
            VALUES ('SV010', 'ATTT', 1, CAST(GETDATE() AS date), 9.5);
        END
    """))

    conn.execute(text("""
        IF NOT EXISTS (SELECT 1 FROM BANGDIEM WHERE MASV = 'SV013' AND MAMH = 'CNPM' AND LAN = 1)
        BEGIN
            DECLARE @question_json_cnpm nvarchar(max);
            DECLARE @answer_json_cnpm nvarchar(max);

            SELECT @question_json_cnpm = N'[' + STRING_AGG(CONVERT(nvarchar(20), CAUHOI), N',') + N']'
            FROM (
                SELECT TOP (30) CAUHOI
                FROM BODE
                WHERE MAMH = 'CNPM' AND TRINHDO IN ('B', 'C')
                ORDER BY CAUHOI
            ) q;

            SELECT @answer_json_cnpm = N'{' + STRING_AGG(CONCAT(N'"', CAUHOI, N'":"', CASE WHEN DAP_AN = 'B' THEN 'B' ELSE 'A' END, N'"'), N',') + N'}'
            FROM (
                SELECT TOP (30) CAUHOI, DAP_AN
                FROM BODE
                WHERE MAMH = 'CNPM' AND TRINHDO IN ('B', 'C')
                ORDER BY CAUHOI
            ) q;

            INSERT INTO PHIENTHI (
                MASV, MALOP, MAMH, TRINHDO, LAN, SOCAUTHI, THOIGIAN, NGAYTHI,
                BATDAU_LUC, THOIGIAN_CONLAI, TRANGTHAI, DANHSACH_CAUHOI,
                DAPAN_DACHON, CAUHOI_HIENTAI, CAPNHAT_LUC, NOPBAI_LUC, DIEM
            )
            VALUES (
                'SV013', 'D23CQCN02', 'CNPM', 'B', 1, 30, 25, CAST(GETDATE() AS date),
                DATEADD(MINUTE, -25, GETDATE()), 0, N'DA_NOP', @question_json_cnpm,
                @answer_json_cnpm, 29, GETDATE(), GETDATE(), 8
            );

            INSERT INTO BANGDIEM (MASV, MAMH, LAN, NGAYTHI, DIEM)
            VALUES ('SV013', 'CNPM', 1, CAST(GETDATE() AS date), 8);
        END
    """))

print("More demo data seeded successfully")

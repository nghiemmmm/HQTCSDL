USE hqtcsdl;
GO

/* Demo accounts
   PGV:      PGV001 / 123456
   Teacher:  GV001 / 123456
   Teacher:  GV002 / 123456
   Student:  SV001 / 123456
   Student:  SV002 / 123456
   Student:  SV003 / 123456
*/

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'PGV') CREATE ROLE [PGV];
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'GIANGVIEN') CREATE ROLE [GIANGVIEN];
GO

IF NOT EXISTS (SELECT 1 FROM MONHOC WHERE MAMH = 'CSDL')
    INSERT INTO MONHOC (MAMH, TENMH) VALUES ('CSDL', N'Co so du lieu');
IF NOT EXISTS (SELECT 1 FROM MONHOC WHERE MAMH = 'MMT')
    INSERT INTO MONHOC (MAMH, TENMH) VALUES ('MMT', N'Mang may tinh');
GO

IF NOT EXISTS (SELECT 1 FROM LOP WHERE MALOP = 'D21CQCN01')
    INSERT INTO LOP (MALOP, TENLOP) VALUES ('D21CQCN01', N'Dai hoc CNTT 01');
IF NOT EXISTS (SELECT 1 FROM LOP WHERE MALOP = 'D21CQCN02')
    INSERT INTO LOP (MALOP, TENLOP) VALUES ('D21CQCN02', N'Dai hoc CNTT 02');
GO

IF NOT EXISTS (SELECT 1 FROM GIAOVIEN WHERE MAGV = 'PGV001')
    INSERT INTO GIAOVIEN (MAGV, HO, TEN, SODTLL, DIACHI) VALUES ('PGV001', N'Phong', N'GiaoVu', '', '');
IF NOT EXISTS (SELECT 1 FROM GIAOVIEN WHERE MAGV = 'GV001')
    INSERT INTO GIAOVIEN (MAGV, HO, TEN, SODTLL, DIACHI) VALUES ('GV001', N'Nguyen Van', N'An', '', '');
IF NOT EXISTS (SELECT 1 FROM GIAOVIEN WHERE MAGV = 'GV002')
    INSERT INTO GIAOVIEN (MAGV, HO, TEN, SODTLL, DIACHI) VALUES ('GV002', N'Tran Thi', N'Binh', '', '');
GO

IF NOT EXISTS (SELECT 1 FROM SINHVIEN WHERE MASV = 'SV001')
    INSERT INTO SINHVIEN (MASV, HO, TEN, NGAYSINH, DIACHI, MALOP, PASSWORD)
    VALUES ('SV001', N'Le Minh', N'Quan', '2003-02-15', N'TP HCM', 'D21CQCN01', '123456');
IF NOT EXISTS (SELECT 1 FROM SINHVIEN WHERE MASV = 'SV002')
    INSERT INTO SINHVIEN (MASV, HO, TEN, NGAYSINH, DIACHI, MALOP, PASSWORD)
    VALUES ('SV002', N'Pham Ngoc', N'Mai', '2003-07-20', N'Dong Nai', 'D21CQCN01', '123456');
IF NOT EXISTS (SELECT 1 FROM SINHVIEN WHERE MASV = 'SV003')
    INSERT INTO SINHVIEN (MASV, HO, TEN, NGAYSINH, DIACHI, MALOP, PASSWORD)
    VALUES ('SV003', N'Hoang Anh', N'Tu', '2003-11-08', N'Binh Duong', 'D21CQCN02', '123456');
GO

DECLARE @login sysname, @password nvarchar(255), @user sysname, @role sysname, @sql nvarchar(max);

DECLARE account_cursor CURSOR LOCAL FAST_FORWARD FOR
SELECT login_name, password_value, user_name, role_name
FROM (VALUES
    ('PGV001', '123456', 'PGV001', 'PGV'),
    ('GV001',  '123456', 'GV001',  'GIANGVIEN'),
    ('GV002',  '123456', 'GV002',  'GIANGVIEN')
) AS accounts(login_name, password_value, user_name, role_name);

OPEN account_cursor;
FETCH NEXT FROM account_cursor INTO @login, @password, @user, @role;
WHILE @@FETCH_STATUS = 0
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = @login)
    BEGIN
        SET @sql = N'CREATE LOGIN ' + QUOTENAME(@login)
            + N' WITH PASSWORD = ' + QUOTENAME(@password, '''')
            + N', DEFAULT_DATABASE = [hqtcsdl], CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF';
        EXEC(@sql);
    END
    ELSE
    BEGIN
        SET @sql = N'ALTER LOGIN ' + QUOTENAME(@login)
            + N' WITH PASSWORD = ' + QUOTENAME(@password, '''')
            + N', DEFAULT_DATABASE = [hqtcsdl], CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF';
        EXEC(@sql);
    END

    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = @user)
    BEGIN
        SET @sql = N'CREATE USER ' + QUOTENAME(@user) + N' FOR LOGIN ' + QUOTENAME(@login);
        EXEC(@sql);
    END

    IF NOT EXISTS (
        SELECT 1
        FROM sys.database_role_members drm
        JOIN sys.database_principals rp ON drm.role_principal_id = rp.principal_id
        JOIN sys.database_principals up ON drm.member_principal_id = up.principal_id
        WHERE rp.name = @role AND up.name = @user
    )
    BEGIN
        SET @sql = N'ALTER ROLE ' + QUOTENAME(@role) + N' ADD MEMBER ' + QUOTENAME(@user);
        EXEC(@sql);
    END

    FETCH NEXT FROM account_cursor INTO @login, @password, @user, @role;
END
CLOSE account_cursor;
DEALLOCATE account_cursor;
GO

DECLARE @i int;

SET @i = 1;
WHILE @i <= 8
BEGIN
    IF NOT EXISTS (SELECT 1 FROM BODE WHERE MAMH = 'CSDL' AND TRINHDO = 'A' AND NOIDUNG = CONCAT(N'CSDL A cau ', @i))
        INSERT INTO BODE (MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN, MAGV)
        VALUES ('CSDL', 'A', CONCAT(N'CSDL A cau ', @i), N'Dap an A', N'Dap an B', N'Dap an C', N'Dap an D', 'A', 'GV001');
    SET @i += 1;
END

SET @i = 1;
WHILE @i <= 5
BEGIN
    IF NOT EXISTS (SELECT 1 FROM BODE WHERE MAMH = 'CSDL' AND TRINHDO = 'B' AND NOIDUNG = CONCAT(N'CSDL B cau ', @i))
        INSERT INTO BODE (MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN, MAGV)
        VALUES ('CSDL', 'B', CONCAT(N'CSDL B cau ', @i), N'Dap an A', N'Dap an B', N'Dap an C', N'Dap an D', 'B', 'GV001');
    SET @i += 1;
END

SET @i = 1;
WHILE @i <= 10
BEGIN
    IF NOT EXISTS (SELECT 1 FROM BODE WHERE MAMH = 'CSDL' AND TRINHDO = 'C' AND NOIDUNG = CONCAT(N'CSDL C cau ', @i))
        INSERT INTO BODE (MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN, MAGV)
        VALUES ('CSDL', 'C', CONCAT(N'CSDL C cau ', @i), N'Dap an A', N'Dap an B', N'Dap an C', N'Dap an D', 'C', 'GV001');
    SET @i += 1;
END

SET @i = 1;
WHILE @i <= 10
BEGIN
    IF NOT EXISTS (SELECT 1 FROM BODE WHERE MAMH = 'MMT' AND TRINHDO = 'B' AND NOIDUNG = CONCAT(N'MMT B cau ', @i))
        INSERT INTO BODE (MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN, MAGV)
        VALUES ('MMT', 'B', CONCAT(N'MMT B cau ', @i), N'Dap an A', N'Dap an B', N'Dap an C', N'Dap an D', 'D', 'GV002');
    SET @i += 1;
END
GO

IF NOT EXISTS (SELECT 1 FROM GIAOVIEN_DANGKY WHERE MALOP = 'D21CQCN01' AND MAMH = 'CSDL' AND LAN = 1)
    INSERT INTO GIAOVIEN_DANGKY (MALOP, MAMH, LAN, MAGV, TRINHDO, NGAYTHI, SOCAUTHI, THOIGIAN)
    VALUES ('D21CQCN01', 'CSDL', 1, 'GV001', 'A', DATEADD(MINUTE, -15, GETDATE()), 10, 15);

IF NOT EXISTS (SELECT 1 FROM GIAOVIEN_DANGKY WHERE MALOP = 'D21CQCN02' AND MAMH = 'MMT' AND LAN = 1)
    INSERT INTO GIAOVIEN_DANGKY (MALOP, MAMH, LAN, MAGV, TRINHDO, NGAYTHI, SOCAUTHI, THOIGIAN)
    VALUES ('D21CQCN02', 'MMT', 1, 'GV002', 'B', DATEADD(DAY, 1, GETDATE()), 10, 15);
GO

IF NOT EXISTS (SELECT 1 FROM BANGDIEM WHERE MASV = 'SV001' AND MAMH = 'CSDL' AND LAN = 1)
BEGIN
    DECLARE @question_json nvarchar(max);
    DECLARE @answer_json nvarchar(max);

    SELECT @question_json = N'[' + STRING_AGG(CONVERT(nvarchar(20), CAUHOI), N',') + N']'
    FROM (
        SELECT TOP (10) CAUHOI
        FROM BODE
        WHERE MAMH = 'CSDL' AND TRINHDO IN ('A', 'B')
        ORDER BY CAUHOI
    ) q;

    SELECT @answer_json = N'{' + STRING_AGG(CONCAT(N'"', CAUHOI, N'":"', DAP_AN, N'"'), N',') + N'}'
    FROM (
        SELECT TOP (10) CAUHOI, DAP_AN
        FROM BODE
        WHERE MAMH = 'CSDL' AND TRINHDO IN ('A', 'B')
        ORDER BY CAUHOI
    ) q;

    INSERT INTO PHIENTHI (
        MASV, MALOP, MAMH, TRINHDO, LAN, SOCAUTHI, THOIGIAN, NGAYTHI,
        BATDAU_LUC, THOIGIAN_CONLAI, TRANGTHAI, DANHSACH_CAUHOI,
        DAPAN_DACHON, CAUHOI_HIENTAI, CAPNHAT_LUC, NOPBAI_LUC, DIEM
    )
    VALUES (
        'SV001', 'D21CQCN01', 'CSDL', 'A', 1, 10, 15, CAST(GETDATE() AS date),
        DATEADD(MINUTE, -4, GETDATE()), 60, N'DA_NOP', @question_json,
        @answer_json, 0, GETDATE(), GETDATE(), 10
    );

    INSERT INTO BANGDIEM (MASV, MAMH, LAN, NGAYTHI, DIEM)
    VALUES ('SV001', 'CSDL', 1, CAST(GETDATE() AS date), 10);
END
GO

SELECT 'Demo data seeded successfully' AS Message;
GO



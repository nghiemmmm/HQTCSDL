SP liên quan đến điểm : 
1. Nếu muốn giáo viên xem toàn bộ sinh viên trong lớp, kể cả sinh viên chưa thi / chưa có điểm: 
CREATE PROC SP_GET_BANGDIEM_MONHOC
    @MALOP NCHAR(15),
    @MAMH  NCHAR(5),
    @LAN   SMALLINT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        sv.MASV,
        sv.HO,
        sv.TEN,
        bd.DIEM
    FROM SINHVIEN sv
    LEFT JOIN BANGDIEM bd 
        ON sv.MASV = bd.MASV
        AND bd.MAMH = @MAMH
        AND bd.LAN = @LAN
    WHERE 
        sv.MALOP = @MALOP
    ORDER BY 
        sv.TEN ASC, 
        sv.HO ASC;
END
2. muốn xem những sinh viên đã có điểm : 
CREATE PROC SP_GET_BANGDIEM_MONHOC
    @MALOP NCHAR(15),
    @MAMH  NCHAR(5),
    @LAN   SMALLINT
AS
BEGIN
    SELECT 
        bd.MASV,
        sv.HO,
        sv.TEN,
        bd.DIEM
    FROM BANGDIEM bd
    INNER JOIN SINHVIEN sv 
        ON sv.MASV = bd.MASV
    WHERE 
        bd.MAMH = @MAMH
        AND bd.LAN = @LAN
        AND sv.MALOP = @MALOP;
END
3. SP_GET_CauHoi dùng để lấy câu hỏi thi theo môn, trình độ và số câu thi : 

```sql
CREATE PROC SP_GET_CauHoi
    @mamh NCHAR(5),
    @trinhDo CHAR(1),
    @socauthi INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @TrinhDoDuoi CHAR(1);

    SET @TrinhDoDuoi =
        CASE 
            WHEN @trinhDo = 'A' THEN 'B'
            WHEN @trinhDo = 'B' THEN 'C'
            ELSE NULL
        END;

    DECLARE @countCauHoi INT;
    DECLARE @countCauHoiDuoi INT = 0;

    SELECT @countCauHoi = COUNT(*)
    FROM BODE
    WHERE MAMH = @mamh 
      AND TRINHDO = @trinhDo;

    IF @TrinhDoDuoi IS NOT NULL
    BEGIN
        SELECT @countCauHoiDuoi = COUNT(*)
        FROM BODE
        WHERE MAMH = @mamh 
          AND TRINHDO = @TrinhDoDuoi;
    END

    DECLARE @SoCauLowerCanBu INT = 0;
    DECLARE @MaxLowerCanBu INT = @socauthi * 30 / 100;

    IF @countCauHoi < @socauthi
    BEGIN
        SET @SoCauLowerCanBu = @socauthi - @countCauHoi;

        IF @TrinhDoDuoi IS NULL
        BEGIN
            RAISERROR(N'Không đủ câu hỏi và không thể bù trình độ dưới.', 16, 1);
            RETURN;
        END

        IF @SoCauLowerCanBu > @MaxLowerCanBu
        BEGIN
            RAISERROR(N'Số câu cần bù vượt quá giới hạn 30%.', 16, 1);
            RETURN;
        END

        IF @countCauHoiDuoi < @SoCauLowerCanBu
        BEGIN
            RAISERROR(N'Không đủ câu hỏi trình độ dưới để bù.', 16, 1);
            RETURN;
        END
    END

    DECLARE @SoCauPrimaryCanLay INT = @socauthi - @SoCauLowerCanBu;

    SELECT *
    FROM (
        SELECT TOP (@SoCauPrimaryCanLay)
            CAUHOI, MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN
        FROM BODE
        WHERE MAMH = @mamh 
          AND TRINHDO = @trinhDo
        ORDER BY NEWID()
    ) AS PrimaryQuestions

    UNION ALL

    SELECT *
    FROM (
        SELECT TOP (@SoCauLowerCanBu)
            CAUHOI, MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN
        FROM BODE
        WHERE MAMH = @mamh 
          AND TRINHDO = @TrinhDoDuoi
        ORDER BY NEWID()
    ) AS LowerQuestions;
END
```
Bản 2 đơn giản lấy câu hỏi thi : 
```sql
AS
BEGIN
	DECLARE @countCauHoi int, @countCauHoiSiteKhac int, @TrinhDoDuoi nchar(1),
	 @countCauHoiDuoi int, @countCHDuoiSiteKhac int
	--Trình độ A
	IF(@trinhDo = 'A')
	BEGIN 
		SET @TrinhDoDuoi = 'B'
	END
	--Trình độ B
	ELSE IF(@trinhDo = 'B')
	BEGIN 
		SET @TrinhDoDuoi = 'C'
	END
	IF(@trinhDo = 'C')
...
```
Bảng chi tiet bai thi : 
CREATE TABLE [dbo].[CT_BAITHI](
	[MAMH] [char](5) NOT NULL,
	[MASV] [char](8) NOT NULL,
	[LAN] [smallint] NOT NULL,
	[MACH] [int] NOT NULL,
	[DAP_AN_CHON] [nchar](1) NULL,
	[rowguid] [uniqueidentifier] ROWGUIDCOL  NOT NULL,
 CONSTRAINT [PK_CT_BAITHI] PRIMARY KEY CLUSTERED 
(
	[MAMH] ASC,
	[MASV] ASC,
	[LAN] ASC,
	[MACH] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] 
SP SP_GET_CT_BAITHI dùng để lấy chi tiết bài thi đã làm của một sinh viên. : 
## 3. `SP_GET_CT_BAITHI`
**Parameters:** `@MASV char(8), @MAMH char(5), @LAN smallint`

**Key Logic Snippet:**
```sql
AS
BEGIN
	select CH.CAUHOI, A, B, C, D, DAP_AN, NOIDUNG, DAP_AN_CHON from (SELECT CAUHOI, A, B, C, D, DAP_AN, NOIDUNG FROM BODE
		WHERE MAMH = @MAMH) CH INNER JOIN 
	(SELECT MACH, DAP_AN_CHON FROM CT_BAITHI WHERE MASV = @MASV AND MAMH = @MAMH AND  LAN = @LAN) CT
	ON CH.CAUHOI = CT.MACH
END
```
SP lấy toàn bộ câu hỏi của phiên thi + đáp án sinh viên đã chọn từ bảng PHIENTHI :
CREATE PROC SP_GET_CT_BAITHI_FROM_PHIENTHI
    @MASV CHAR(8),
    @MAMH CHAR(5),
    @LAN  SMALLINT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        b.CAUHOI,
        b.NOIDUNG,
        b.A,
        b.B,
        b.C,
        b.D,
        b.DAP_AN,
        DAP_AN_CHON =
            JSON_VALUE(
                pt.dapan_dachon,
                '$."' + CAST(b.CAUHOI AS VARCHAR(20)) + '"'
            )
    FROM PHIENTHI pt
    CROSS APPLY OPENJSON(pt.danhsach_cauhoi) q
    INNER JOIN BODE b
        ON b.CAUHOI = TRY_CAST(q.[value] AS INT)
    WHERE
        pt.masv = @MASV
        AND pt.mamh = @MAMH
        AND pt.lan = @LAN
        AND b.MAMH = @MAMH
    ORDER BY
        TRY_CAST(q.[key] AS INT);
END
GO

User Defined Function (UDF) : 
CREATE FUNCTION [dbo].[Check_Lop_MH_Da_Thi]
(
    @MAMH nchar(5),
    @MALOP nchar(15),
    @LAN smallint
)
RETURNS nchar(1)

CREATE FUNCTION dbo.Check_Lop_MH_Da_Thi
(	
    @MAMH NCHAR(5),
    @MALOP NCHAR(15),
    @LAN SMALLINT
)
RETURNS NCHAR(1)
AS
BEGIN 
    DECLARE @checked NCHAR(1);

    IF EXISTS
    (
        SELECT 1
        FROM SINHVIEN sv
        INNER JOIN BANGDIEM bd
            ON bd.MASV = sv.MASV
        WHERE sv.MALOP = @MALOP
          AND bd.MAMH = @MAMH
          AND bd.LAN = @LAN
    )
        SET @checked = N'X';
    ELSE 
        SET @checked = N'';

    RETURN @checked;
END
GO

Lấy danh sách các kỳ thi/lịch thi mà giáo viên đã đăng ký trong một khoảng thời gian. : 
CREATE PROC SP_GET_DS_GVDK
    @FROM DATETIME,
    @TO   DATETIME
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        l.TENLOP,
        mh.TENMH,
        HOTEN = gv.HO + N' ' + gv.TEN,
        gvdk.SOCAUTHI,
        gvdk.NGAYTHI,
        DATHI = dbo.Check_Lop_MH_Da_Thi(gvdk.MAMH, gvdk.MALOP, gvdk.LAN)
    FROM GIAOVIEN_DANGKY gvdk
    INNER JOIN LOP l
        ON l.MALOP = gvdk.MALOP
    INNER JOIN MONHOC mh
        ON mh.MAMH = gvdk.MAMH
    INNER JOIN GIAOVIEN gv
        ON gv.MAGV = gvdk.MAGV
    WHERE
        gvdk.NGAYTHI >= @FROM
        AND gvdk.NGAYTHI < @TO
    ORDER BY
        gvdk.NGAYTHI ASC;
END
GO

Tìm các giáo viên:

Có trong bảng GIAOVIEN
Nhưng chưa được cấp tài khoản đăng nhập : 
CREATE PROC SP_GET_GV_CHUA_DK
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        gv.MAGV,
        HOTEN = gv.HO + N' ' + gv.TEN
    FROM GIAOVIEN gv
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM sys.sysmembers sm
        INNER JOIN sys.sysusers role_user
            ON role_user.uid = sm.groupuid
        INNER JOIN sys.sysusers member_user
            ON member_user.uid = sm.memberuid
        WHERE role_user.name IN ('TRUONG', 'GIANGVIEN')
          AND member_user.name = gv.MAGV
    );
END
GO 

Lấy thông tin một lịch thi (đăng ký thi) cụ thể của giáo viên. : 
CREATE PROC SP_GET_GVDK
    @MALOP NCHAR(15),
    @MAMH NCHAR(5),
    @LAN SMALLINT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        MAGV,
        MALOP,
        MAMH,
        TRINHDO,
        LAN,
        NGAYTHI,
        SOCAUTHI,
        THOIGIAN
    FROM GIAOVIEN_DANGKY
    WHERE MALOP = @MALOP
      AND MAMH = @MAMH
      AND LAN = @LAN;
END
GO 
## 7. `SP_GET_MH_DATHI_SV`
**Parameters:** `@MASV char(8)`

**Key Logic Snippet:**
```sql
AS
BEGIN
	SELECT DISTINCT MAMH, TENMH = (SELECT TENMH FROM MONHOC WHERE MAMH = BD.MAMH) FROM BANGDIEM AS BD WHERE MASV = @MASV
END
```

---
Lấy mật khẩu của sinh viên từ mã sinh viên.
CREATE PROC SP_GET_PASSWORD_FROM_MASV
    @maSV NCHAR(8)
AS
BEGIN
    SELECT PASSWORD
    FROM SINHVIEN
    WHERE MASV = @maSV
END
## 9. `SP_INSERT_KQ_THI`
**Parameters:** `@BAITHI TYPE_CT_BAITHI READONLY, @MASV nchar(8), @MAMH nchar(5), @LAN smallint, @NGAYTHI datetime, @DIEM float`

**Key Logic Snippet:**
```sql
AS  
BEGIN  
	SET XACT_ABORT ON;
	BEGIN TRANSACTION
	BEGIN TRY
		INSERT INTO BANGDIEM(MASV, MAMH, LAN, NGAYTHI, DIEM) VALUES(@MASV, @MAMH, @LAN, @NGAYTHI, @DIEM)
		INSERT INTO CT_BAITHI(MASV, MAMH, LAN, MACH, DAP_AN_CHON) SELECT MASV, MAMH, LAN, MACH, NULLIF(DAP_AN_CHON,'') FROM @BAITHI  
		COMMIT
	END TRY
	BEGIN CATCH
		 ROLLBACK
		 DECLARE @ErrorMessage VARCHAR(100)
		 SELECT @ErrorMessage = 'Lỗi: ' + ERROR_MESSAGE()
		 RAISERROR(@ErrorMessage, 16, 1)
	END CATCH
...
```

---

## 10. `SP_KT_Bo_De_Ton_Tai`
**Parameters:** `@MACH int`

**Key Logic Snippet:**
```sql
AS
IF exists(select * from dbo.BODE where CAUHOI = @MACH)
	raiserror ('Mã câu hỏi đã tồn tại, vui lòng nhập lại',16,1)
```

---
CREATE PROC SP_KT_Giao_Vien_Ton_Tai
    @MAGV NCHAR(8)
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS
    (
        SELECT 1
        FROM GIAOVIEN
        WHERE MAGV = @MAGV
    )
    BEGIN
        RAISERROR(
            N'Mã GV đã tồn tại, vui lòng chọn mã khác',
            16,
            1
        );
    END
END
GO
SP này dùng để:

Kiểm tra sinh viên đã thi một môn học ở một lần thi cụ thể hay chưa. : 
CREATE PROC SP_KT_Lan_Thi
    @MASV NCHAR(8),
    @MAMH NCHAR(5),
    @LAN SMALLINT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS
    (
        SELECT 1
        FROM BANGDIEM
        WHERE MASV = @MASV
          AND MAMH = @MAMH
          AND LAN = @LAN
    )
        SELECT '1';
    ELSE
        SELECT '0';
END
GO
## 15. `sp_KT_Lop_Da_Thi`
**Parameters:** None

**Key Logic Snippet:**
```sql
as
begin
	IF EXISTS(SELECT bdl.MASV 
	From
		(Select sv.MASV From SINHVIEN sv
		 Where (sv.MALOP = @MALOP)) As lsv
	   Inner Join
		(Select bd.MASV 
		 From  BANGDIEM bd
		 Where (bd.MAMH = @MAMH AND bd.LAN = @LAN )) As bdl 
	   On lsv.MASV = bdl.MASV) 
	   SELECT '1'
	ELSE SELECT '0'
end
```
SP này dùng để:

Kiểm tra lớp học có bị trùng mã lớp hoặc trùng tên lớp hay không trước khi thêm mới.
CREATE PROC SP_KT_Lop_Ton_Tai
    @MALOP  NCHAR(15),
    @TENLOP NVARCHAR(40)
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS
    (
        SELECT 1
        FROM LOP
        WHERE MALOP = @MALOP
    )
        SELECT 1 AS KETQUA;

    ELSE IF EXISTS
    (
        SELECT 1
        FROM LOP
        WHERE TENLOP = @TENLOP
    )
        SELECT 2 AS KETQUA;

    ELSE
        SELECT 0 AS KETQUA;
END
GO
Kiểm tra môn học có bị trùng mã môn học hoặc trùng tên môn học hay không trước khi thêm mới. : 
CREATE PROC SP_KT_MonHoc_Ton_Tai
    @MAMH CHAR(5),
    @TENMH NVARCHAR(40)
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS
    (
        SELECT 1
        FROM MONHOC
        WHERE MAMH = @MAMH
    )
        SELECT 1 AS KETQUA;

    ELSE IF EXISTS
    (
        SELECT 1
        FROM MONHOC
        WHERE TENMH = @TENMH
    )
        SELECT 2 AS KETQUA;

    ELSE
        SELECT 0 AS KETQUA;
END
GO
Kiểm tra khi sửa môn học, tên môn học mới có bị trùng với môn học khác hay không. : 
CREATE PROC SP_KT_Sua_MonHoc_Ton_Tai
    @MAMH CHAR(5),
    @TENMH NVARCHAR(40)
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS
    (
        SELECT 1
        FROM MONHOC
        WHERE TENMH = @TENMH
          AND MAMH <> @MAMH
    )
    BEGIN
        RAISERROR(
            N'Tên môn học đã tồn tại, vui lòng nhập tên khác',
            16,
            1
        );
    END
END
GO
Sửa / khôi phục lại thông tin một câu hỏi trong bảng BODE. 
CREATE PROC SP_Phuc_Hoi_Sua_Bo_De
    @MACH INT,
    @MAMH NCHAR(5),
    @MAGV NCHAR(8),
    @TRINHDO NCHAR(1),
    @DAPAN NCHAR(1),
    @NOIDUNG NTEXT,
    @A NTEXT,
    @B NTEXT,
    @C NTEXT,
    @D NTEXT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE dbo.BODE
    SET 
        MAMH = @MAMH,
        MAGV = @MAGV,
        TRINHDO = @TRINHDO,
        DAP_AN = @DAPAN,
        NOIDUNG = @NOIDUNG,
        A = @A,
        B = @B,
        C = @C,
        D = @D
    WHERE CAUHOI = @MACH;

    SELECT '0' AS KETQUA;
END
GO

1. SP_GET_CauHoi
   Lấy câu hỏi theo môn, trình độ, số câu thi
   ========================================================= */
CREATE PROC SP_GET_CauHoi
    @mamh NCHAR(5),
    @trinhDo CHAR(1),
    @socauthi INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @TrinhDoDuoi CHAR(1);

    SET @TrinhDoDuoi =
        CASE 
            WHEN @trinhDo = 'A' THEN 'B'
            WHEN @trinhDo = 'B' THEN 'C'
            ELSE NULL
        END;

    DECLARE @countCauHoi INT;
    DECLARE @countCauHoiDuoi INT = 0;

    SELECT @countCauHoi = COUNT(*)
    FROM BODE
    WHERE MAMH = @mamh 
      AND TRINHDO = @trinhDo;

    IF @TrinhDoDuoi IS NOT NULL
    BEGIN
        SELECT @countCauHoiDuoi = COUNT(*)
        FROM BODE
        WHERE MAMH = @mamh 
          AND TRINHDO = @TrinhDoDuoi;
    END

    DECLARE @SoCauLowerCanBu INT = 0;
    DECLARE @MaxLowerCanBu INT = @socauthi * 30 / 100;

    IF @countCauHoi < @socauthi
    BEGIN
        SET @SoCauLowerCanBu = @socauthi - @countCauHoi;

        IF @TrinhDoDuoi IS NULL
        BEGIN
            RAISERROR(N'Không đủ câu hỏi và không thể bù trình độ dưới.', 16, 1);
            RETURN;
        END

        IF @SoCauLowerCanBu > @MaxLowerCanBu
        BEGIN
            RAISERROR(N'Số câu cần bù vượt quá giới hạn 30%.', 16, 1);
            RETURN;
        END

        IF @countCauHoiDuoi < @SoCauLowerCanBu
        BEGIN
            RAISERROR(N'Không đủ câu hỏi trình độ dưới để bù.', 16, 1);
            RETURN;
        END
    END

    DECLARE @SoCauPrimaryCanLay INT = @socauthi - @SoCauLowerCanBu;

    SELECT *
    FROM (
        SELECT TOP (@SoCauPrimaryCanLay)
            CAUHOI, MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN
        FROM BODE
        WHERE MAMH = @mamh 
          AND TRINHDO = @trinhDo
        ORDER BY NEWID()
    ) AS PrimaryQuestions

    UNION ALL

    SELECT *
    FROM (
        SELECT TOP (@SoCauLowerCanBu)
            CAUHOI, MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN
        FROM BODE
        WHERE MAMH = @mamh 
          AND TRINHDO = @TrinhDoDuoi
        ORDER BY NEWID()
    ) AS LowerQuestions;
END
GO
mới 
    -- Lấy ngẫu nhiên câu hỏi chính và câu hỏi bù, sau đó trộn đều chúng lại
    SELECT * FROM (
        SELECT *
        FROM (
            SELECT TOP (@SoCauPrimaryCanLay)
                CAUHOI, MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN
            FROM BODE
            WHERE MAMH = @mamh 
              AND TRINHDO = @trinhDo
            ORDER BY NEWID()
        ) AS PrimaryQuestions

        UNION ALL

        SELECT *
        FROM (
            SELECT TOP (@SoCauLowerCanBu)
                CAUHOI, MAMH, TRINHDO, NOIDUNG, A, B, C, D, DAP_AN
            FROM BODE
            WHERE MAMH = @mamh 
              AND TRINHDO = @TrinhDoDuoi
            ORDER BY NEWID()
        ) AS LowerQuestions
    ) AS CombinedResult
    ORDER BY NEWID(); -- Sắp xếp ngẫu nhiên toàn bộ đề thi một lần cuối
END
GO
 2. SP_GET_BANGDIEM_MONHOC
   Lấy bảng điểm môn học của cả lớp
   ========================================================= */
CREATE PROC SP_GET_BANGDIEM_MONHOC
    @MALOP NCHAR(15),
    @MAMH  NCHAR(5),
    @LAN   SMALLINT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        sv.MASV,
        sv.HO,
        sv.TEN,
        bd.DIEM
    FROM SINHVIEN sv
    LEFT JOIN BANGDIEM bd 
        ON sv.MASV = bd.MASV
        AND bd.MAMH = @MAMH
        AND bd.LAN = @LAN
    WHERE 
        sv.MALOP = @MALOP
    ORDER BY 
        sv.TEN ASC, 
        sv.HO ASC;
END
GO
/* =========================================================
   4. SP_KT_Lan_Thi
   Kiểm tra sinh viên đã thi môn/lần đó chưa
   ========================================================= */
CREATE PROC SP_KT_Lan_Thi
    @MASV NCHAR(8),
    @MAMH NCHAR(5),
    @LAN SMALLINT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS
    (
        SELECT 1
        FROM BANGDIEM
        WHERE MASV = @MASV
          AND MAMH = @MAMH
          AND LAN = @LAN
    )
        SELECT CAST(1 AS BIT) AS DATHI;
    ELSE
        SELECT CAST(0 AS BIT) AS DATHI;
END
GO
/* =========================================================
   5. SP_INSERT_KQ_THI
   Nộp bài: cập nhật PHIENTHI và ghi điểm vào BANGDIEM
   ========================================================= */
CREATE PROC SP_INSERT_KQ_THI
    @PHIENTHI_ID INT,
    @DIEM FLOAT,
    @DAPAN_DACHON NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRANSACTION;

    BEGIN TRY
        UPDATE PHIENTHI
        SET 
            dapan_dachon = @DAPAN_DACHON,
            diem = @DIEM,
            trangthai = N'DA_NOP',
            nopbai_luc = GETDATE(),
            capnhat_luc = GETDATE()
        WHERE id = @PHIENTHI_ID
          AND trangthai = N'DANG_LAM';

        IF @@ROWCOUNT = 0
        BEGIN
            RAISERROR(N'Phiên thi không tồn tại hoặc không ở trạng thái đang làm.', 16, 1);
            ROLLBACK;
            RETURN;
        END

        INSERT INTO BANGDIEM(MASV, MAMH, LAN, NGAYTHI, DIEM)
        SELECT 
            masv,
            mamh,
            lan,
            CAST(GETDATE() AS DATE),
            @DIEM
        FROM PHIENTHI
        WHERE id = @PHIENTHI_ID;

        COMMIT;
    END TRY
    BEGIN CATCH
        ROLLBACK;
        THROW;
    END CATCH
END
GO
/* =========================================================
   7. SP_GET_GVDK
   Lấy thông tin một lịch thi cụ thể
   ========================================================= */
CREATE PROC SP_GET_GVDK
    @MALOP NCHAR(15),
    @MAMH NCHAR(5),
    @LAN SMALLINT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        MAGV,
        MALOP,
        MAMH,
        TRINHDO,
        LAN,
        NGAYTHI,
        SOCAUTHI,
        THOIGIAN
    FROM GIAOVIEN_DANGKY
    WHERE MALOP = @MALOP
      AND MAMH = @MAMH
      AND LAN = @LAN;
END
GO




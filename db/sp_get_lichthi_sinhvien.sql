USE [THITRACNGHIEM]
GO

CREATE OR ALTER PROC dbo.SP_GET_LICHTHI_SINHVIEN
    @MASV NCHAR(8)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Today DATE = CAST(GETDATE() AS DATE);

    SELECT
        MAMH = RTRIM(GVDK.MAMH),
        TENMH = MH.TENMH,
        LAN = GVDK.LAN,
        NGAYTHI = GVDK.NGAYTHI,
        SOCAUTHI = GVDK.SOCAUTHI,
        THOIGIAN = GVDK.THOIGIAN,
        TRANGTHAI =
            CASE
                WHEN BD.MASV IS NOT NULL
                    THEN NCHAR(272) + NCHAR(227) + N' thi'
                WHEN CAST(GVDK.NGAYTHI AS DATE) > @Today
                    THEN N'Ch' + NCHAR(432) + N'a ' + NCHAR(273)
                         + NCHAR(7871) + N'n ng' + NCHAR(224) + N'y thi'
                WHEN CAST(GVDK.NGAYTHI AS DATE) = @Today
                    THEN NCHAR(272) + NCHAR(432) + NCHAR(7907)
                         + N'c thi h' + NCHAR(244) + N'm nay'
                ELSE NCHAR(272) + NCHAR(227) + N' qu' + NCHAR(225)
                     + N' h' + NCHAR(7841) + N'n'
            END,
        DUOC_BAT_DAU_THI =
            CONVERT(bit,
                CASE
                    WHEN BD.MASV IS NULL
                         AND CAST(GVDK.NGAYTHI AS DATE) = @Today
                    THEN 1
                    ELSE 0
                END
            )
    FROM SINHVIEN SV
    INNER JOIN GIAOVIEN_DANGKY GVDK
        ON GVDK.MALOP = SV.MALOP
    INNER JOIN MONHOC MH
        ON MH.MAMH = GVDK.MAMH
    LEFT JOIN BANGDIEM BD
        ON BD.MASV = SV.MASV
       AND BD.MAMH = GVDK.MAMH
       AND BD.LAN = GVDK.LAN
    WHERE SV.MASV = @MASV
    ORDER BY GVDK.NGAYTHI DESC, GVDK.MAMH, GVDK.LAN;
END
GO

/*
Suggested supporting indexes:

CREATE INDEX IX_SINHVIEN_MALOP
ON dbo.SINHVIEN(MALOP);

CREATE INDEX IX_GVDK_MALOP_NGAYTHI
ON dbo.GIAOVIEN_DANGKY(MALOP, NGAYTHI)
INCLUDE (MAMH, LAN, SOCAUTHI, THOIGIAN);

-- Skip this if BANGDIEM already has primary key (MASV, MAMH, LAN).
CREATE INDEX IX_BANGDIEM_MASV_MAMH_LAN
ON dbo.BANGDIEM(MASV, MAMH, LAN);
*/

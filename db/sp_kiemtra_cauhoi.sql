CREATE PROCEDURE SP_KiemTraSoLuongCauHoi
    @MAMH NCHAR(5),
    @TRINHDO CHAR(1),
    @SOCAUTHI SMALLINT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @SoCauCoSan INT;

    -- Đếm số lượng câu hỏi hiện có trong BODE theo môn học và trình độ
    SELECT @SoCauCoSan = COUNT(CAUHOI)
    FROM BODE
    WHERE MAMH = @MAMH AND TRINHDO = @TRINHDO;

    -- Trả về kết quả kiểm tra
    IF @SoCauCoSan >= @SOCAUTHI
    BEGIN
        SELECT 
            1 AS IsHopLe, 
            @SoCauCoSan AS SoCauCoSan, 
            N'Đủ câu hỏi thi' AS ThongBao;
    END
    ELSE
    BEGIN
        SELECT 
            0 AS IsHopLe, 
            @SoCauCoSan AS SoCauCoSan, 
            N'Không đủ câu hỏi. Yêu cầu: ' + CAST(@SOCAUTHI AS NVARCHAR) + N', Hiện có: ' + CAST(@SoCauCoSan AS NVARCHAR) AS ThongBao;
    END
END
GO

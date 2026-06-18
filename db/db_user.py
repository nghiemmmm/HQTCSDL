from urllib import response

from core.templates import Jinja2Templates
from sqlalchemy.orm.session import Session
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from db.database import engine
from schemas.schemas import DangNhap, DangKy
from core.session import create_session
from fastapi.responses import Response

templates = Jinja2Templates(directory="templates")

# def dang_nhap(db: Session, request: DangNhap):
#     print(f"Đăng nhập với username: {request.username}, role: {request.role}")
#     if request.role == "GIANGVIEN":

#         # kiểm tra login tồn tại bằng Stored Procedure (SP_KiemTraLogin)
#         query = text("EXEC SP_KiemTraLogin @login_name = :login_name")
#         result = db.execute(query, {"login_name": request.username}).fetchone()

#         if result is None:
#             raise HTTPException(
#                 status_code=404,
#                 detail={
#                     "field": "username",
#                     "message": "Tài khoản không tồn tại"
#                 }
#             )

#         # thử đăng nhập SQL Server
#         try:

#             connection_url = URL.create(
#                 "mssql+pyodbc",
#                 username=request.username,
#                 password=request.password,
#                 host="localhost",
#                 port=1433,
#                 database="THITRACNGHIEM",
#                 query={
#                     "driver": "ODBC Driver 18 for SQL Server",
#                     "TrustServerCertificate": "yes"
#                 },
#             )

#             engine = create_engine(connection_url)
#             conn = engine.connect()

#         except Exception:
#             raise HTTPException(
#                 status_code=401,
#                  detail={
#                     "field": "password",
#                     "message": "Sai mật khẩu SQL Server"
#                 }
#             )

#         # lấy database user (MAGV)
#         # query = text("""
#         #     SELECT USER_NAME() AS MAGV
#         # """)

#         # user = conn.execute(query).fetchone()

#         # # lấy thông tin giảng viên
#         # query = text("""
#         #     SELECT HO,TEN
#         #     FROM GIAOVIEN
#         #     WHERE MAGV = :magv
#         # """)

      
#         query = text("EXEC dbo.sp_ThongTinDangNhap :tenlogin")

#         result = conn.execute(query, {
#             "tenlogin": request.username
#         }).fetchone()
#         if result is None:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Không lấy được thông tin đăng nhập"
#             )

#         hoten = (result.Hoten or "").strip().split()
#         ho = " ".join(hoten[:-1]) if len(hoten) > 1 else ""
#         ten = hoten[-1] if hoten else ""

#         return {
#             "ma": result.Username,
#             "ho": ho,
#             "ten": ten,
#             "role": result.Rolename
#         }


   
#     elif request.role == "SINHVIEN":
#         query_exists = text("""
#             SELECT MASV
#             FROM SINHVIEN
#             WHERE MASV = :masv
#         """)

#         sv_exists = conn.execute(
#             query_exists,
#             {"masv": request.username}
#         ).fetchone()

#         if sv_exists is None:
#             conn.close()
#             raise HTTPException(
#                 status_code=404,
#                 detail={
#                     "field": "username",
#                     "message": "Mã sinh viên không tồn tại"
#                 }
#             )

#         query_login = text("""
#             SELECT MASV, HO, TEN
#             FROM SINHVIEN
#             WHERE MASV = :masv AND PASSWORD = :password
#         """)

#         sv = conn.execute(
#             query_login,
#             {"masv": request.username, "password": "123"}
#         ).fetchone()

#         conn.close()

#         try:
#             connection_url = URL.create(
#                 "mssql+pyodbc",
#                 username="sa",
#                 password="123",
#                 host="localhost",
#                 port=1433,
#                 database="THITRACNGHIEM",
#                 query={
#                     "driver": "ODBC Driver 18 for SQL Server",
#                     "TrustServerCertificate": "yes"
#                 },
#             )

#             engine = create_engine(connection_url)
#             conn = engine.connect()

#         except Exception:
#             raise HTTPException(
#                 status_code=500,
#                 detail={
#                     "field": "system",
#                     "message": "Không thể kết nối database"
#                 }
#             )
#         return {
#             "ma": sv.MASV,
#             "ho": sv.HO,
#             "ten": sv.TEN,
#             "role": "SINHVIEN"
#         }

#     else:
#         raise HTTPException(
#             status_code=400,
#             detail="Role không hợp lệ"
#         )
    
def dang_nhap(db: Session, request: DangNhap):

    print(f"Login: {request.username} - {request.role}")

    # ================= GIANG VIEN =================
    if request.role in ("GIANGVIEN", "PGV"):

        try:
            query = text("EXEC SP_KiemTraLogin @login_name = :login_name")
            result = db.execute(query, {"login_name": request.username}).fetchone()
        except Exception:
            result = db.execute(
                text("SELECT name FROM sys.server_principals WHERE name = :login_name"),
                {"login_name": request.username}
            ).fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "field": "username",
                    "message": "Tài khoản không tồn tại"
                }
            )

        try:
            connection_url = URL.create(
                "mssql+pyodbc",
                username=request.username,
                password=request.password,
                host="localhost\\SQLEXPRESS",
                database="hqtcsdl",
                query={
                    "driver": "ODBC Driver 18 for SQL Server",
                    "TrustServerCertificate": "yes"
                },
            )

            engine = create_engine(connection_url)
            conn = engine.connect()

        except Exception:
            requested_role = request.role.value if hasattr(request.role, "value") else str(request.role)
            password_ok = db.execute(
                text("""
                    SELECT CASE
                        WHEN PWDCOMPARE(:password, password_hash) = 1 THEN 1
                        ELSE 0
                    END
                    FROM sys.sql_logins
                    WHERE name = :username
                """),
                {"username": request.username, "password": request.password}
            ).scalar()

            if password_ok == 1:
                result = db.execute(
                    text("""
                        SELECT
                            gv.MAGV AS Username,
                            LTRIM(RTRIM(COALESCE(gv.HO, '') + ' ' + COALESCE(gv.TEN, ''))) AS Hoten,
                            COALESCE(role_info.Rolename, :requested_role) AS Rolename
                        FROM GIAOVIEN gv
                        OUTER APPLY (
                            SELECT TOP 1 role_principal.name AS Rolename
                            FROM sys.database_role_members drm
                            JOIN sys.database_principals role_principal
                                ON drm.role_principal_id = role_principal.principal_id
                            JOIN sys.database_principals user_principal
                                ON drm.member_principal_id = user_principal.principal_id
                            WHERE user_principal.name = :username
                              AND role_principal.name IN ('PGV', 'GIANGVIEN')
                            ORDER BY CASE role_principal.name WHEN 'PGV' THEN 1 ELSE 2 END
                        ) role_info
                        WHERE gv.MAGV = :username
                    """),
                    {"username": request.username, "requested_role": requested_role}
                ).fetchone()

                if result is not None:
                    hoten = (result.Hoten or "").strip().split()
                    ho = " ".join(hoten[:-1]) if len(hoten) > 1 else ""
                    ten = hoten[-1] if hoten else ""
                    return {
                        "ma": result.Username,
                        "ho": ho,
                        "ten": ten,
                        "role": result.Rolename
                    }

            raise HTTPException(
                status_code=401,
                detail={
                    "field": "password",
                    "message": "Sai mật khẩu SQL Server"
                }
            )

        try:
            query = text("EXEC dbo.sp_ThongTinDangNhap :tenlogin")
            result = conn.execute(query, {
                "tenlogin": request.username
            }).fetchone()
        except Exception:
            result = conn.execute(
                text("""
                    SELECT
                        gv.MAGV AS Username,
                        LTRIM(RTRIM(COALESCE(gv.HO, '') + ' ' + COALESCE(gv.TEN, ''))) AS Hoten,
                        CASE
                            WHEN IS_ROLEMEMBER('PGV') = 1 THEN 'PGV'
                            WHEN IS_ROLEMEMBER('GIANGVIEN') = 1 THEN 'GIANGVIEN'
                            ELSE :requested_role
                        END AS Rolename
                    FROM GIAOVIEN gv
                    WHERE gv.MAGV = :username
                """),
                {"username": request.username, "requested_role": str(request.role)}
            ).fetchone()

        conn.close()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "field": "system",
                    "message": "Không lấy được thông tin đăng nhập"
                }
            )

        hoten = (result.Hoten or "").strip().split()
        ho = " ".join(hoten[:-1]) if len(hoten) > 1 else ""
        ten = hoten[-1] if hoten else ""

        user_data = {
            # "user_id": result.Username,
            "ma": result.Username,
            "ho": ho,
            "ten": ten,
            "role": result.Rolename
        }
        return user_data

    # ================= SINH VIEN =================
    elif request.role == "SINHVIEN":

        # check tồn tại
        query_exists = text("""
            SELECT MASV
            FROM SINHVIEN
            WHERE MASV = :masv
        """)

        sv_exists = db.execute(
            query_exists,
            {"masv": request.username}
        ).fetchone()

        if sv_exists is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "field": "username",
                    "message": "Mã sinh viên không tồn tại"
                }
            )

        # check login
        query_login = text("""
            SELECT MASV, HO, TEN
            FROM SINHVIEN
            WHERE MASV = :masv AND PASSWORD = :password
        """)

        sv = db.execute(
            query_login,
            {
                "masv": request.username,
                "password": request.password
            }
        ).fetchone()

        if sv is None:
            raise HTTPException(
                status_code=401,
                detail={
                    "field": "password",
                    "message": "Sai mật khẩu"
                }
            )

        # return {
        #     "ma": sv.MASV,
        #     "ho": sv.HO,
        #     "ten": sv.TEN,
        #     "role": "SINHVIEN"
        # 
        user_data = {
            "ma": sv.MASV,
            "ho": sv.HO,
            "ten": sv.TEN,
            "role": "SINHVIEN",
        }
        return user_data

    # ================= ROLE INVALID =================
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "role",
                "message": "Role không hợp lệ"
            }
        )
    
def _dang_ky_legacy(db: Session, request: DangKy):
    if request.role == "SINHVIEN":
        raise HTTPException(
            status_code=400,
            detail="Chuc nang tao tai khoan chi ap dung cho PGV va giang vien"
        )


def dang_ky(db: Session, request: DangKy):
    role_name = request.role.value if hasattr(request.role, "value") else str(request.role)
    if role_name == "SINHVIEN":
        raise HTTPException(
            status_code=400,
            detail="Chuc nang tao tai khoan chi ap dung cho PGV va giang vien"
        )

    if role_name not in ("PGV", "GIANGVIEN"):
        raise HTTPException(status_code=400, detail="Nhom quyen khong hop le")

    ma_nv = (request.username or request.loginname or "").strip().upper()
    hoten = (request.hoten or "").strip()
    teacher = db.execute(
        text("SELECT MAGV FROM GIAOVIEN WHERE MAGV = :magv"),
        {"magv": ma_nv}
    ).fetchone()
    if teacher is None:
        if not hoten:
            raise HTTPException(
                status_code=400,
                detail="Vui long nhap ho va ten nhan vien"
            )

        parts = hoten.split()
        ho = " ".join(parts[:-1]) if len(parts) > 1 else ""
        ten = parts[-1] if parts else hoten
        db.execute(
            text("""
                INSERT INTO GIAOVIEN (MAGV, HO, TEN, SODTLL, DIACHI)
                VALUES (:magv, :ho, :ten, '', '')
            """),
            {"magv": ma_nv, "ho": ho, "ten": ten}
        )
        db.commit()

    existing_login = db.execute(
        text("SELECT name FROM sys.server_principals WHERE name = :loginname"),
        {"loginname": request.loginname}
    ).fetchone()
    if existing_login is not None:
        raise HTTPException(
            status_code=400,
            detail="Tai khoan nay da ton tai"
        )

    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(
                text("""
                    DECLARE @login_name sysname = :loginname;
                    DECLARE @user_name sysname = :username;
                    DECLARE @role_name sysname = :role_name;
                    DECLARE @password nvarchar(255) = :password;
                    DECLARE @sql nvarchar(max);

                    IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = @login_name)
                    BEGIN
                        SET @sql = N'CREATE LOGIN ' + QUOTENAME(@login_name)
                            + N' WITH PASSWORD = ' + QUOTENAME(@password, '''')
                            + N', DEFAULT_DATABASE = [hqtcsdl], CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF';
                        EXEC(@sql);
                    END
                    ELSE
                    BEGIN
                        SET @sql = N'ALTER LOGIN ' + QUOTENAME(@login_name)
                            + N' WITH PASSWORD = ' + QUOTENAME(@password, '''')
                            + N', DEFAULT_DATABASE = [hqtcsdl], CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF';
                        EXEC(@sql);
                    END

                    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = @user_name)
                    BEGIN
                        SET @sql = N'CREATE USER ' + QUOTENAME(@user_name)
                            + N' FOR LOGIN ' + QUOTENAME(@login_name);
                        EXEC(@sql);
                    END

                    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = @role_name)
                    BEGIN
                        SET @sql = N'CREATE ROLE ' + QUOTENAME(@role_name);
                        EXEC(@sql);
                    END

                    IF NOT EXISTS (
                        SELECT 1
                        FROM sys.database_role_members drm
                        JOIN sys.database_principals role_principal
                            ON drm.role_principal_id = role_principal.principal_id
                        JOIN sys.database_principals user_principal
                            ON drm.member_principal_id = user_principal.principal_id
                        WHERE role_principal.name = @role_name
                          AND user_principal.name = @user_name
                    )
                    BEGIN
                        SET @sql = N'ALTER ROLE ' + QUOTENAME(@role_name)
                            + N' ADD MEMBER ' + QUOTENAME(@user_name);
                        EXEC(@sql);
                    END
                """),
                {
                    "loginname": request.loginname,
                    "password": request.password,
                    "username": ma_nv,
                    "role_name": role_name,
                }
            )

        return {"message": "Tao tai khoan thanh cong"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Loi khi tao tai khoan: {str(e)}"
        )
    
    # Map system_role → SQL Server role
    sql_role = ""
    if request.role in ("GIANGVIEN", "PGV"):
        sql_role = "db_owner"  # ✅ Role tồn tại trong SQL Server
    else:
        sql_role = "db_datareader"  # ✅ Role tồn tại trong SQL Server
    
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(
                text("""
                EXEC sp_TaoTaiKhoan
                    :loginname,
                    :password,
                    :username,
                    :role
                """),
                {
                    "loginname": request.loginname,
                    "password": request.password,
                    "username": request.username,
                    "role": sql_role
                }
            )
        
        return {
            "message": "Tạo tài khoản thành công"
        }   
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo tài khoản: {str(e)}"
        )

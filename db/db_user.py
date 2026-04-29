from sqlalchemy.orm.session import Session
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from db.database import engine
from schemas.schemas import DangNhap, DangKy


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
    if request.role == "GIANGVIEN":

        query = text("EXEC SP_KiemTraLogin @login_name = :login_name")
        result = db.execute(query, {"login_name": request.username}).fetchone()

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
                host="localhost",
                port=1433,
                database="THITRACNGHIEM",
                query={
                    "driver": "ODBC Driver 18 for SQL Server",
                    "TrustServerCertificate": "yes"
                },
            )

            engine = create_engine(connection_url)
            conn = engine.connect()

        except Exception:
            raise HTTPException(
                status_code=401,
                detail={
                    "field": "password",
                    "message": "Sai mật khẩu SQL Server"
                }
            )

        query = text("EXEC dbo.sp_ThongTinDangNhap :tenlogin")

        result = conn.execute(query, {
            "tenlogin": request.username
        }).fetchone()

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

        return {
            "ma": result.Username,
            "ho": ho,
            "ten": ten,
            "role": result.Rolename
        }

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

        return {
            "ma": sv.MASV,
            "ho": sv.HO,
            "ten": sv.TEN,
            "role": "SINHVIEN"
        }

    # ================= ROLE INVALID =================
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "role",
                "message": "Role không hợp lệ"
            }
        )
    
def dang_ky(db: Session, request: DangKy):
    
    # Map system_role → SQL Server role
    sql_role = ""
    if request.system_role == "GIANGVIEN":
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
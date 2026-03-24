from sqlalchemy.orm.session import Session
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from db.database import engine
from schemas.schemas import DangNhapBase, UserBase, DangKyBase


def dang_nhap(db: Session, request: DangNhapBase):
    print(f"Đăng nhập với username: {request.username}, role: {request.role}")
    if request.role == "GIANGVIEN":

        # kiểm tra login tồn tại
        query = text("""
            SELECT name
            FROM sys.server_principals
            WHERE name = :login_name
            AND type_desc = 'SQL_LOGIN'
        """)

        result = db.execute(query, {"login_name": request.username}).fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Login không tồn tại"
            )

        # thử đăng nhập SQL Server
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
                detail="Sai mật khẩu SQL Server"
            )

        # lấy database user (MAGV)
        query = text("""
            SELECT USER_NAME() AS MAGV
        """)

        user = conn.execute(query).fetchone()

        # lấy thông tin giảng viên
        query = text("""
            SELECT HO,TEN
            FROM GIAOVIEN
            WHERE MAGV = :magv
        """)

        # gv = conn.execute(query, {"magv": user.MAGV}).fetchone()

        # conn.close()

        # if gv is None:
        #     raise HTTPException(
        #         status_code=404,
        #         detail="Không tìm thấy giảng viên"
        #     )
        # return {
        #     "ma": user.MAGV,
        #     "ho": gv.HO,
        #     "ten": gv.TEN
        # }
        query = text("EXEC dbo.sp_ThongTinDangNhap :tenlogin")

        result = conn.execute(query, {
            "tenlogin": request.username
        }).fetchone()
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Không lấy được thông tin đăng nhập"
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


   
    elif request.role == "SINHVIEN":

        try:
            connection_url = URL.create(
                "mssql+pyodbc",
                username="sa",
                password="123",
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
                detail="Không thể kết nối bằng login sinh viên"
            )

        # kiểm tra mã sinh viên
        query = text("""
            SELECT MASV, HO, TEN
            FROM SINHVIEN
            WHERE MASV = :masv
        """)

        sv = conn.execute(query, {"masv": request.username}).fetchone()
        conn.close()

        if sv is None:
            raise HTTPException(
                status_code=404,
                detail="Mã sinh viên không tồn tại"
            )
        return {
            "ma": sv.MASV,
            "ho": sv.HO,
            "ten": sv.TEN,
            "role": "SINHVIEN"
        }

    else:
        raise HTTPException(
            status_code=400,
            detail="Role không hợp lệ"
        )
    

    
def dang_ky(db: Session, request: DangKyBase):

    # Normalize hoten - xóa multiple spaces
    hoten_normalized = ' '.join(request.hoten.split())
    
    result = db.execute(
        text("""
        SELECT MAGV
        FROM GIAOVIEN
        WHERE REPLACE(RTRIM(HO) + ' ' + RTRIM(TEN), '  ', ' ') = :hoten
        """),
        {"hoten": hoten_normalized}
    ).fetchone()
    
    print(f"Tìm kiếm: {hoten_normalized}")
    print(f"Kết quả: {result}")
    
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy giảng viên")

    magv = result.MAGV.strip()
    
    # Map system_role → SQL Server role
    sql_role = ""
    if request.system_role == "ADMIN":
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
                    "username": magv,
                    "role": sql_role
                }
            )
        
        return {"message": "Đăng ký thành công"}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo tài khoản: {str(e)}"
        )
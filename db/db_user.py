"""User repository and SQL Server account persistence operations."""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import Session

from db.database import engine


def find_sql_login(db: Session, login_name: str):
    """Return a SQL login row when it exists."""
    return db.execute(
        text("EXEC SP_KiemTraLogin @login_name = :login_name"),
        {"login_name": login_name},
    ).fetchone()


def connect_as_user(username: str, password: str):
    """Open a SQL Server connection using supplied credentials."""
    connection_url = URL.create(
        "mssql+pyodbc",
        username=username,
        password=password,
        host="localhost",
        port=1433,
        database="THITRACNGHIEM",
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "TrustServerCertificate": "yes",
        },
    )
    return create_engine(connection_url).connect()


def get_login_profile(connection, login_name: str):
    """Return profile data for a SQL login."""
    return connection.execute(
        text("EXEC dbo.sp_ThongTinDangNhap :tenlogin"),
        {"tenlogin": login_name},
    ).fetchone()


def find_student(db: Session, student_id: str):
    """Return a student identity row."""
    return db.execute(
        text("SELECT MASV FROM SINHVIEN WHERE MASV = :masv"),
        {"masv": student_id},
    ).fetchone()


def authenticate_student(db: Session, student_id: str, password: str):
    """Return a student profile when credentials match."""
    return db.execute(
        text(
            """
            SELECT MASV, HO, TEN
            FROM SINHVIEN
            WHERE MASV = :masv AND PASSWORD = :password
            """
        ),
        {"masv": student_id, "password": password},
    ).fetchone()


def create_sql_account(
    login_name: str,
    password: str,
    username: str,
    sql_role: str,
    database_engine: Engine = engine,
) -> None:
    """Create a SQL Server account through the existing procedure."""
    with database_engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as connection:
        connection.execute(
            text(
                """
                EXEC sp_TaoTaiKhoan
                    :loginname,
                    :password,
                    :username,
                    :role
                """
            ),
            {
                "loginname": login_name,
                "password": password,
                "username": username,
                "role": sql_role,
            },
        )

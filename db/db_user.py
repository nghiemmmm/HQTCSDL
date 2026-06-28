"""User repository and SQL Server account persistence operations."""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import Session

from db.database import DB_DRIVER, DB_HOST, DB_NAME, DB_PORT, engine


def find_sql_login(db: Session, login_name: str):
    """Return a SQL login row when it exists in the current database."""
    return db.execute(
        text(
            """
            SELECT name
            FROM sys.database_principals
            WHERE name = :login_name
              AND type IN ('S', 'U')
            """
        ),
        {"login_name": login_name},
    ).fetchone()




def is_integrated_security_only(db: Session) -> bool:
    """Return True when SQL Server only allows Windows Authentication."""
    value = db.execute(
        text("SELECT CAST(SERVERPROPERTY('IsIntegratedSecurityOnly') AS INT)")
    ).scalar()
    return bool(value)
def connect_as_user(username: str, password: str):
    """Open a SQL Server connection using supplied SQL credentials."""
    connection_url = URL.create(
        "mssql+pyodbc",
        username=username,
        password=password,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        query={
            "driver": DB_DRIVER,
            "TrustServerCertificate": "yes",
        },
    )
    return create_engine(connection_url).connect()


def get_login_profile(connection, login_name: str):
    """Return profile data for a SQL login without requiring stored procedures."""
    return connection.execute(
        text(
            """
            SELECT
                Username = principal.name,
                Hoten = COALESCE(NULLIF(LTRIM(RTRIM(gv.HO + N' ' + gv.TEN)), N''), principal.name),
                Rolename = CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM sys.database_role_members drm
                        INNER JOIN sys.database_principals role_principal
                            ON role_principal.principal_id = drm.role_principal_id
                        WHERE drm.member_principal_id = principal.principal_id
                          AND role_principal.name = N'PGV'
                    ) THEN N'PGV'
                    WHEN EXISTS (
                        SELECT 1
                        FROM sys.database_role_members drm
                        INNER JOIN sys.database_principals role_principal
                            ON role_principal.principal_id = drm.role_principal_id
                        WHERE drm.member_principal_id = principal.principal_id
                          AND role_principal.name = N'GIANGVIEN'
                    ) THEN N'GIANGVIEN'
                    ELSE N'GIANGVIEN'
                END
            FROM sys.database_principals principal
            LEFT JOIN GIAOVIEN gv
                ON LTRIM(RTRIM(gv.MAGV)) = principal.name
            WHERE principal.name = :login_name
            """
        ),
        {"login_name": login_name},
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



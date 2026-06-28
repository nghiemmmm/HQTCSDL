import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from file import password

DB_USER = os.getenv("DB_USER", password.DB_USER)
DB_PASSWORD = os.getenv("DB_PASSWORD", str(password.DB_PASSWORD))
DB_HOST = os.getenv("DB_HOST", r"localhost\SQLEXPRESS")
DB_PORT_VALUE = os.getenv("DB_PORT", "").strip()
DB_PORT = int(DB_PORT_VALUE) if DB_PORT_VALUE else None
DB_NAME = os.getenv("DB_NAME", "hqtcsdl")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower() in {
    "1",
    "true",
    "yes",
}

query = {
    "driver": DB_DRIVER,
    "TrustServerCertificate": "yes",
}

if DB_TRUSTED_CONNECTION:
    query["Trusted_Connection"] = "yes"
    connection_username = None
    connection_password = None
else:
    connection_username = DB_USER
    connection_password = DB_PASSWORD

connection_url = URL.create(
    "mssql+pyodbc",
    username=connection_username,
    password=connection_password,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query=query,
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=20,
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

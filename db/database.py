# Import thư viện
import socket
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import URL
from file import password

# Lấy địa chỉ IP của máy chủ bằng socket
MY_HOSTNAME = socket.gethostname()
MY_IP_ADDR = socket.gethostbyname(MY_HOSTNAME)

# Cấu trúc chuỗi kết nối đến SQL Server
# connection_url = URL.create(
#     "mssql+pyodbc",
#     username=password.DB_USER, # Tên đăng nhập 
#     password=password.DB_PASSWORD, # mật khẩu đăng nhập
#     host="localhost\\SQLEXPRESS",  # Kết nối đến SQL Express local
#     database= password.DB_NAME, # Tên của database cần truy cập
#     query={
#         "driver": "ODBC Driver 18 for SQL Server",
#         "TrustServerCertificate": "yes"
#     },
# )

connection_url = "mssql+pyodbc://localhost\\SQLEXPRESS/hqtcsdl?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=20,
)

# Tạo một nhà máy (sessionmaker) tự động tạo các Session
# Khi sử dụng scoped_session, bạn sẽ có một session riêng biệt cho mỗi luồng hoặc yêu cầu,
# và chúng sẽ không bị xung đột với nhau. Đây là cách an toàn và hiệu quả để quản lý session trong các ứng dụng web đa luồng.
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Khai báo cơ sở dữ liệu với SQLAlchemy
Base = declarative_base()

# Hàm lấy session cho mỗi request, khi gọi các lệnh đến Database thì cần gọi hàm này để mở kết nối đến Database
# Hàm này sẽ tự động đóng kết nối sau khi sử dụng xong
def get_db():
    """
    Mở một kết nối đến SQL Server để thực hiện các thao tác CRUD
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from enum import Enum

class UserRoleEnum(str, Enum):
    tochuc = "PGV"
    student = "SINHVIEN"
    teacher = "GIANGVIEN"
    staff = "PGV"  # Phòng giáo vụ


# =====================================
# Role for System (Quyền hệ thống)
# =====================================
class SystemRoleEnum(str, Enum):
    """Role trong hệ thống - xác định quyền truy cập"""
    admin = "ADMIN"
    user = "USER"


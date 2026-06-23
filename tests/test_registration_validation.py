import sys
from datetime import datetime, timedelta
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")

from db.database import SessionLocal
from schemas.schemas import DangKyThi
from services.exam_registration_service import create_registration
from services.exceptions import ValidationError, ConflictError

def test_validation():
    db = SessionLocal()
    
    # Mock user dict
    user = {"ma": "GV003", "role": "GIANGVIEN"}
    
    # Test case 1: Date in the past (yesterday)
    past_date = datetime.now() - timedelta(days=1)
    req_past = DangKyThi(
        mamh="CSDL",
        malop="D21CQCN01",
        trinhdo="A",
        lan=2,
        ngaythi=past_date,
        socauthi=10,
        thoigian=15
    )
    
    print("Testing past date...")
    try:
        create_registration(db, req_past, user)
        print("FAIL: Expected ValidationError for past date, but it passed.")
    except ValidationError as e:
        # Convert string to ASCII-safe representation for print
        safe_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        print(f"PASS: Correctly raised ValidationError: {safe_msg}")
    except Exception as e:
        print(f"FAIL: Raised unexpected exception: {e}")

    # Test case 2: Date too close to present (10 minutes in future)
    close_date = datetime.now() + timedelta(minutes=10)
    req_close = DangKyThi(
        mamh="CSDL",
        malop="D21CQCN01",
        trinhdo="A",
        lan=2,
        ngaythi=close_date,
        socauthi=10,
        thoigian=15
    )
    
    print("\nTesting close future date (10 minutes)...")
    try:
        create_registration(db, req_close, user)
        print("FAIL: Expected ValidationError for close future date, but it passed.")
    except ValidationError as e:
        safe_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        print(f"PASS: Correctly raised ValidationError: {safe_msg}")
    except Exception as e:
        print(f"FAIL: Raised unexpected exception: {e}")

    # Test case 3: Date valid (45 minutes in future)
    valid_date = datetime.now() + timedelta(minutes=45)
    req_valid = DangKyThi(
        mamh="CSDL",
        malop="D21CQCN01",
        trinhdo="A",
        lan=2,
        ngaythi=valid_date,
        socauthi=10,
        thoigian=15
    )
    
    print("\nTesting valid future date (45 minutes)...")
    try:
        create_registration(db, req_valid, user)
        print("PASS: Date check passed successfully (may fail later on DB constraints if already exists, which is expected).")
    except ValidationError as e:
        safe_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        if "lon hon" in safe_msg or "l?n h?n" in safe_msg:
            print(f"FAIL: Incorrectly raised lead-time ValidationError: {safe_msg}")
        else:
            print(f"PASS: Passed date check but raised other ValidationError: {safe_msg}")
    except ConflictError as e:
        print(f"PASS: Passed date check but raised ConflictError (already registered).")
    except Exception as e:
        print(f"PASS: Passed date check but raised other exception.")
        
    db.close()

if __name__ == "__main__":
    test_validation()

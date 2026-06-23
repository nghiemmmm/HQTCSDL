import sys
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")

from db.database import SessionLocal
from services.exam_service import list_available_subjects, list_available_classes

def main():
    db = SessionLocal()
    
    # Test for GV003 who registered ATTT for class D23CQCN01
    user_gv003 = {"ma": "GV003", "role": "GIANGVIEN"}
    
    print("--- TESTING GV003 PRACTICE SUBJECTS & CLASSES ---")
    subjects = list_available_subjects(db, user_gv003)
    classes = list_available_classes(db, user_gv003)
    
    print("Subjects found:")
    for sj in subjects:
        mamh = sj.mamh.strip()
        tenmh = sj.tenmh.strip().encode('ascii', errors='replace').decode('ascii')
        print(f" - {mamh}: {tenmh}")
        
    print("\nClasses found:")
    for cl in classes:
        malop = cl.malop.strip()
        tenlop = cl.tenlop.strip().encode('ascii', errors='replace').decode('ascii')
        print(f" - {malop}: {tenlop}")
        
    # Validation assertion
    has_attt = any(sj.mamh.strip() == "ATTT" for sj in subjects)
    has_d23 = any(cl.malop.strip() == "D23CQCN01" for cl in classes)
    
    if has_attt and has_d23 and len(subjects) == 1 and len(classes) == 1:
        print("\nPASS: Correctly filtered to only 1 subject (ATTT) and 1 class (D23CQCN01) for GV003.")
    else:
        print("\nFAIL: Mismatch in expected results.")
        
    db.close()

if __name__ == "__main__":
    main()

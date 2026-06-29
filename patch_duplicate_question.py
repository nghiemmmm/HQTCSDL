import re

# 1. Update db_bode.py
with open('db/db_bode.py', 'r', encoding='utf-8') as f:
    db_code = f.read()

new_get_mamh = """def get_by_mamh(db: Session, mamh: str) -> list[DbBoDe]:
    \"\"\"Return questions by subject code.\"\"\"
    return db.query(DbBoDe).filter(DbBoDe.mamh == mamh).all()

def create_bode"""

if 'def get_by_mamh' not in db_code:
    db_code = db_code.replace("def create_bode", new_get_mamh)
    with open('db/db_bode.py', 'w', encoding='utf-8') as f:
        f.write(db_code)


# 2. Update question_service.py
with open('services/question_service.py', 'r', encoding='utf-8') as f:
    svc_code = f.read()

# Add ConflictError to imports if not there
if 'ConflictError' not in svc_code:
    svc_code = re.sub(r'(from services\.exceptions import \([\s\S]*?)(\))', r'\1    ConflictError,\n\2', svc_code)

# Add _check_duplicate_question
check_func = """def _check_duplicate_question(
    db: Session,
    mamh: str,
    noidung: str,
    a: str,
    b: str,
    c: str,
    d: str,
    exclude_id: int | None = None
) -> None:
    questions = db_bode.get_by_mamh(db, mamh)
    req_noidung = (noidung or "").strip().casefold()
    req_answers = {
        _normalize_answer(a),
        _normalize_answer(b),
        _normalize_answer(c),
        _normalize_answer(d)
    }

    for q in questions:
        if exclude_id and q.cauhoi == exclude_id:
            continue
            
        q_noidung = (q.noidung or "").strip().casefold()
        if q_noidung != req_noidung:
            continue
            
        q_answers = {
            _normalize_answer(q.a),
            _normalize_answer(q.b),
            _normalize_answer(q.c),
            _normalize_answer(q.d)
        }
        
        if req_answers == q_answers:
            raise ConflictError("Câu hỏi này đã tồn tại trong bộ đề của môn học (trùng nội dung và 4 đáp án).")

def create_question"""

if 'def _check_duplicate_question' not in svc_code:
    svc_code = svc_code.replace("def create_question", check_func)


# Add validation to create_question
old_create = """def create_question(
    db: Session,
    request: CauHoiCreate,
    user: dict[str, Any],
) -> DbBoDe:
    \"\"\"Create a question, assigning teachers to their own records.\"\"\"
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma", "")
    _validate_unique_answers(request.a, request.b, request.c, request.d)
    try:"""

new_create = """def create_question(
    db: Session,
    request: CauHoiCreate,
    user: dict[str, Any],
) -> DbBoDe:
    \"\"\"Create a question, assigning teachers to their own records.\"\"\"
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma", "")
    _validate_unique_answers(request.a, request.b, request.c, request.d)
    _check_duplicate_question(db, request.mamh, request.noidung, request.a, request.b, request.c, request.d)
    try:"""

svc_code = svc_code.replace(old_create, new_create)


# Add validation to update_question
old_update = """def update_question(
    db: Session,
    question_id: int,
    request: CauHoiUpdate,
    user: dict[str, Any],
) -> DbBoDe:
    \"\"\"Update a question after ownership validation.\"\"\"
    question = _owned_question(db, question_id, user)
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma", "")
    _validate_unique_answers(
        request.a if request.a is not None else question.a,
        request.b if request.b is not None else question.b,
        request.c if request.c is not None else question.c,
        request.d if request.d is not None else question.d,
    )
    try:"""

new_update = """def update_question(
    db: Session,
    question_id: int,
    request: CauHoiUpdate,
    user: dict[str, Any],
) -> DbBoDe:
    \"\"\"Update a question after ownership validation.\"\"\"
    question = _owned_question(db, question_id, user)
    if user.get("role") == "GIANGVIEN":
        request.magv = user.get("ma", "")
    
    a_val = request.a if request.a is not None else question.a
    b_val = request.b if request.b is not None else question.b
    c_val = request.c if request.c is not None else question.c
    d_val = request.d if request.d is not None else question.d
    mamh_val = request.mamh if request.mamh is not None else question.mamh
    noidung_val = request.noidung if request.noidung is not None else question.noidung

    _validate_unique_answers(a_val, b_val, c_val, d_val)
    _check_duplicate_question(db, mamh_val, noidung_val, a_val, b_val, c_val, d_val, exclude_id=question_id)
    try:"""

svc_code = svc_code.replace(old_update, new_update)

with open('services/question_service.py', 'w', encoding='utf-8') as f:
    f.write(svc_code)

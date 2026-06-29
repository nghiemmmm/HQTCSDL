import re

# 1. Update question_service.py
with open('services/question_service.py', 'r', encoding='utf-8') as f:
    service = f.read()

if 'from db import db_monhoc' not in service:
    service = re.sub(r'from db import db_bode, db_giaovien', 'from db import db_bode, db_giaovien, db_monhoc', service)

old_get_page_data = """def get_page_data(db: Session, user: dict[str, Any]) -> dict[str, list]:
    \"\"\"Build the question-page data while enforcing teacher ownership.\"\"\"
    questions = (
        db_bode.get_by_teacher(db, user.get("ma", ""))
        if user.get("role") == "GIANGVIEN"
        else db_bode.get_all_bode(db)
    )
    teachers = db_giaovien.get_all(db)
    return {
        "bodes": [_question_payload(item) for item in questions],
        "giaoviens": [
            {
                "magv": (teacher.magv or "").strip(),
                "hoten": (
                    f"{(teacher.ho or '').strip()} {(teacher.ten or '').strip()}"
                ).strip(),
            }
            for teacher in teachers
        ],
    }"""

new_get_page_data = """def get_page_data(db: Session, user: dict[str, Any]) -> dict[str, list]:
    \"\"\"Build the question-page data while enforcing teacher ownership.\"\"\"
    questions = (
        db_bode.get_by_teacher(db, user.get("ma", ""))
        if user.get("role") == "GIANGVIEN"
        else db_bode.get_all_bode(db)
    )
    teachers = db_giaovien.get_all(db)
    subjects = db_monhoc.list_subjects(db)
    return {
        "bodes": [_question_payload(item) for item in questions],
        "giaoviens": [
            {
                "magv": (teacher.magv or "").strip(),
                "hoten": (
                    f"{(teacher.ho or '').strip()} {(teacher.ten or '').strip()}"
                ).strip(),
            }
            for teacher in teachers
        ],
        "monhocs": [
            {
                "mamh": (subject.mamh or "").strip(),
                "tenmh": (subject.tenmh or "").strip(),
            }
            for subject in subjects
        ],
    }"""

service = service.replace(old_get_page_data, new_get_page_data)

with open('services/question_service.py', 'w', encoding='utf-8') as f:
    f.write(service)

# 2. Update formBoDe.html
with open('templates/formBoDe.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'<input id="maMH" maxlength="5" disabled>', r'<input id="maMH" maxlength="5" list="listMH" placeholder="Chon ma mon hoc..." disabled>', html)

datalist_gv = """  <datalist id="listGV">
    {% for gv in giaoviens %}
    <option value="{{ gv.magv }} - {{ gv.hoten }}"></option>
    {% endfor %}
  </datalist>"""

datalist_mh = """  <datalist id="listGV">
    {% for gv in giaoviens %}
    <option value="{{ gv.magv }} - {{ gv.hoten }}"></option>
    {% endfor %}
  </datalist>
  <datalist id="listMH">
    {% for mh in monhocs %}
    <option value="{{ mh.mamh }}">{{ mh.tenmh }}</option>
    {% endfor %}
  </datalist>"""

html = html.replace(datalist_gv, datalist_mh)
html = re.sub(r'boDe\.js\?v=\d+', 'boDe.js?v=12', html)

with open('templates/formBoDe.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 3. Update boDe.js
with open('static/js/boDe.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_error_logic = """function showError(msg) {
    if (errorText) {
      errorText.style.color = "#dc2626";
      errorText.innerText = msg;
    }
  }
  function showSuccess(msg) {
    if (errorText) {
      errorText.style.color = "#16a34a";
      errorText.innerText = msg;
    }
  }
  function clearError() {
    if (errorText) {
      errorText.innerText = "";
    }
  }"""

new_error_logic = """let errorTimeout;
  function showError(msg) {
    if (errorText) {
      errorText.style.color = "#dc2626";
      errorText.innerText = msg;
      clearTimeout(errorTimeout);
      errorTimeout = setTimeout(() => { errorText.innerText = ""; }, 5000);
    }
  }
  function showSuccess(msg) {
    if (errorText) {
      errorText.style.color = "#16a34a";
      errorText.innerText = msg;
      clearTimeout(errorTimeout);
      errorTimeout = setTimeout(() => { errorText.innerText = ""; }, 5000);
    }
  }
  function clearError() {
    if (errorText) {
      errorText.innerText = "";
      clearTimeout(errorTimeout);
    }
  }"""

js = js.replace(old_error_logic, new_error_logic)

with open('static/js/boDe.js', 'w', encoding='utf-8') as f:
    f.write(js)

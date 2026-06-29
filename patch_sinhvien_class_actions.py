import re

with open('static/js/sinhVien_v27.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update loadSVFromServer to dim buttons if dsSV.length > 0
old_loadSV = """        dsSV = (storedStudents || rows || []).map((item) => normalizeStudent(item, maLop));

        selectedStudentIndex = -1;

        studentCurrentPage = 1;"""

new_loadSV = """        dsSV = (storedStudents || rows || []).map((item) => normalizeStudent(item, maLop));

        selectedStudentIndex = -1;

        studentCurrentPage = 1;
        
        // Dim buttons if class has students
        if (btnClassEdit) {
            btnClassEdit.style.opacity = dsSV.length > 0 ? "0.4" : "1";
        }
        if (btnClassDelete) {
            btnClassDelete.style.opacity = dsSV.length > 0 ? "0.4" : "1";
        }"""
js = js.replace(old_loadSV, new_loadSV)

# 2. Update btnClassEdit.onclick to block edit if class has students
old_edit = """    btnClassEdit.onclick = () => {
        if (!selectedMaLop) {
            alert("Vui lAng ch?n mTt l>p ` hiu ch%nh");
            return;
        }"""
# Using regex for robust matching
edit_pattern = r'btnClassEdit\.onclick\s*=\s*\(\)\s*=>\s*\{[\s\n]*if\s*\(!selectedMaLop\)\s*\{[\s\n]*alert\([^)]+\);[\s\n]*return;[\s\n]*\}'

match = re.search(edit_pattern, js)
if match:
    replacement = match.group(0) + """
        if (dsSV.length > 0) {
            alert("Không thể hiệu chỉnh lớp vì đã có sinh viên");
            return;
        }"""
    js = js.replace(match.group(0), replacement)
else:
    print("Warning: Could not match btnClassEdit block.")

with open('static/js/sinhVien_v27.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'sinhVien_v\d+\.js', 'sinhVien_v28.js', html)

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Class Edit/Delete dimming and validation applied.")

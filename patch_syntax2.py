import re

# I will just take sinhVien_v20.js, and apply the exact patch only for btnDetailEdit

with open('static/js/sinhVien_v20.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Fix the try block in selectStudent
pattern_try = r'try\s*\{\s*const\s*token\s*=\s*localStorage\.getItem\("token"\);\s*if\s*\(token\)\s*\{[\s\S]*?catch\(e\)\s*\{\s*console\.error\("Error check status",\s*e\);\s*\}'
repl_try = r"""try {
            const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`);
            if (res.ok) {
                const status = await res.json();
                if (status.da_thi || status.da_dang_ky) {
                    if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                }
                if (status.da_thi) {
                    if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                }
            }
        } catch(e) { console.error("Error check status", e); }"""

js = re.sub(pattern_try, repl_try, js)

# 2. Find btnDetailEdit.onclick and add the check
# I will use a more specific regex targeting only btnDetailEdit

pattern_edit = r'(btnDetailEdit\.onclick\s*=\s*\(\)\s*=>\s*\{[\s\S]*?currentFormAction\s*=\s*"edit_sv";\s*const\s*student\s*=\s*dsSV\[selectedStudentIndex\];)'

repl_edit = r"""btnDetailEdit.onclick = async () => {
        if (!requireSelectedClass()) return;
        if (selectedStudentIndex < 0 || !dsSV[selectedStudentIndex]) {
            alert("Vui lòng chọn một sinh viên để hiệu chỉnh");
            return;
        }
        
        currentFormAction = "edit_sv";
        const student = dsSV[selectedStudentIndex];
        
        try {
            const checkResponse = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`);
            const checkData = await checkResponse.json();
            if (checkData.da_thi) {
                alert(`Sinh viên này đã thi. Không thể hiệu chỉnh!`);
                return;
            }
        } catch(e) { console.error(e); }"""

# Only replace the top part of btnDetailEdit
js = re.sub(r'btnDetailEdit\.onclick\s*=\s*\(\)\s*=>\s*\{[\s\S]*?const\s*student\s*=\s*dsSV\[selectedStudentIndex\];', repl_edit, js, count=1)

with open('static/js/sinhVien_v23.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
# Note: we are overwriting from v20, but the HTML might point to v22 right now.
# Replace any vX with v23
html = re.sub(r'sinhVien_v\d+\.js(\?v=\d+)?', 'sinhVien_v23.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Re-patched from v20 to v23.")

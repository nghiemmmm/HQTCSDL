import re

with open('static/js/sinhVien_v16.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update hideAllForms
pattern_hide = r'(function hideAllForms\(\)\s*\{[\s\S]*?)(^\})'
repl_hide = r"""\1
    if (btnDetailAdd) btnDetailAdd.style.display = "inline-block";
    if (btnDetailEdit) { btnDetailEdit.disabled = false; btnDetailEdit.style.opacity = "1"; btnDetailEdit.style.cursor = "pointer"; }
    if (btnDetailDelete) { btnDetailDelete.disabled = false; btnDetailDelete.style.opacity = "1"; btnDetailDelete.style.cursor = "pointer"; }
\2"""
js = re.sub(pattern_hide, repl_hide, js, flags=re.MULTILINE)

# 2. Make selectStudent async
js = js.replace('function selectStudent(index) {', 'async function selectStudent(index) {')

# 3. Update selectStudent logic
pattern_select = r'(if\s*\(\s*formSinhVienButtons\s*\)\s*formSinhVienButtons\.style\.display\s*=\s*"none";)'
repl_select = r"""if (formSinhVienButtons) formSinhVienButtons.style.display = "flex";
        if (btnDetailSaveForm) btnDetailSaveForm.style.display = "none";
        if (btnDetailAdd) btnDetailAdd.style.display = "none";
        if (btnDetailEdit) { btnDetailEdit.disabled = false; btnDetailEdit.style.opacity = "1"; btnDetailEdit.style.cursor = "pointer"; }
        if (btnDetailDelete) { btnDetailDelete.disabled = false; btnDetailDelete.style.opacity = "1"; btnDetailDelete.style.cursor = "pointer"; }
        
        try {
            const token = localStorage.getItem("token");
            if (token) {
                const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const status = await res.json();
                    if (status.da_thi) {
                        if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                        if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                    }
                }
            }
        } catch(e) { console.error("Error check status", e); }"""
js = re.sub(pattern_select, repl_select, js)

# 4. Update btnDetailEdit logic
pattern_edit = r'(if\s*\(\s*formSinhVienButtons\s*\)\s*formSinhVienButtons\.style\.display\s*=\s*"flex";)'
repl_edit = r"""\1
        if (btnDetailSaveForm) btnDetailSaveForm.style.display = "block";"""
js = re.sub(pattern_edit, repl_edit, js)

# 5. Update btnDetailAdd logic
pattern_add = r'(if\s*\(\s*formSinhVienButtons\s*\)\s*formSinhVienButtons\.style\.display\s*=\s*"flex";)'
repl_add = r"""\1
        if (btnDetailSaveForm) btnDetailSaveForm.style.display = "block";
        if (btnDetailAdd) btnDetailAdd.style.display = "none";"""
js = re.sub(pattern_add, repl_add, js)

with open('static/js/sinhVien_v17.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v16\.js(\?v=\d+)?', 'sinhVien_v17.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully applied view mode patch 3.")

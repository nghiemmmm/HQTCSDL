import re

with open('static/js/sinhVien_v15.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. selectStudent
pattern_select = r'(if\s*\(\s*student\s*\)\s*\{\s*showSinhVienForm\(\);\s*fillStudentForm\(student\);\s*)(\})'
repl_select = r"""\1
        if (txtMaSV) { txtMaSV.disabled = true; txtMaSV.style.backgroundColor = "#e5e7eb"; }
        if (txtHoTen) { txtHoTen.disabled = true; txtHoTen.style.backgroundColor = "#e5e7eb"; }
        if (txtNgaySinh) { txtNgaySinh.disabled = true; txtNgaySinh.style.backgroundColor = "#e5e7eb"; }
        if (formSinhVienTitle) formSinhVienTitle.innerText = "Thông tin chi tiết sinh viên";
        if (formSinhVienButtons) formSinhVienButtons.style.display = "none";
    \2"""
js = re.sub(pattern_select, repl_select, js)

# 2. btnDetailEdit
pattern_edit = r'(if\s*\(\s*btnDetailSaveForm\s*\)\s*btnDetailSaveForm\.disabled\s*=\s*false;\s*)(showSinhVienForm\(\);)'
repl_edit = r"""\1
        if (formSinhVienTitle) formSinhVienTitle.innerText = "Hiệu chỉnh thông tin sinh viên";
        if (formSinhVienButtons) formSinhVienButtons.style.display = "flex";
        if (txtMaSV) { txtMaSV.style.backgroundColor = "#e5e7eb"; }
        \2"""
js = re.sub(pattern_edit, repl_edit, js)

# 3. btnDetailAdd
pattern_add = r'(renderSelectedStudentInfo\(null\);\s*)(showSinhVienForm\(\);)'
repl_add = r"""\1
        if (txtMaSV) { txtMaSV.disabled = false; txtMaSV.style.backgroundColor = ""; }
        if (txtHoTen) { txtHoTen.disabled = false; txtHoTen.style.backgroundColor = ""; }
        if (txtNgaySinh) { txtNgaySinh.disabled = false; txtNgaySinh.style.backgroundColor = ""; }
        if (formSinhVienTitle) formSinhVienTitle.innerText = "Thêm sinh viên mới";
        if (formSinhVienButtons) formSinhVienButtons.style.display = "flex";
        \2"""
js = re.sub(pattern_add, repl_add, js)

with open('static/js/sinhVien_v16.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v15\.js(\?v=\d+)?', 'sinhVien_v16.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully applied view mode regex patch.")

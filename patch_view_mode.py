import re

# 1. Update HTML
with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<h3 style="margin: 0;">Nhap thong tin sinh vien</h3>', '<h3 style="margin: 0;" id="formSinhVienTitle">Nhap thong tin sinh vien</h3>')
html = html.replace('<div style="display: flex; gap: 10px;">', '<div style="display: flex; gap: 10px;" id="formSinhVienButtons">', 1)

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update JS
with open('static/js/sinhVien_v14.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add consts at the top
js_top = """
const formSinhVienTitle = document.getElementById("formSinhVienTitle");
const formSinhVienButtons = document.getElementById("formSinhVienButtons");
"""
js = js_top + js

# Update selectStudent
old_select = """
    if (student) {
        showSinhVienForm();
        fillStudentForm(student);
    }
"""
new_select = """
    if (student) {
        showSinhVienForm();
        fillStudentForm(student);
        if (txtMaSV) { txtMaSV.disabled = true; txtMaSV.style.backgroundColor = "#e5e7eb"; }
        if (txtHoTen) { txtHoTen.disabled = true; txtHoTen.style.backgroundColor = "#e5e7eb"; }
        if (txtNgaySinh) { txtNgaySinh.disabled = true; txtNgaySinh.style.backgroundColor = "#e5e7eb"; }
        if (formSinhVienTitle) formSinhVienTitle.innerText = "Thông tin chi tiết sinh viên";
        if (formSinhVienButtons) formSinhVienButtons.style.display = "none";
    }
"""
js = js.replace(old_select, new_select)

# Update btnDetailEdit
old_edit = """
        currentFormAction = "edit_sv";
        const student = dsSV[selectedStudentIndex];
        if (txtMaSV) {
            txtMaSV.value = student.maSV;
            txtMaSV.disabled = true;
        }
        if (txtHoTen) { txtHoTen.value = student.hoTen; txtHoTen.disabled = false; txtHoTen.style.backgroundColor = ""; }
        if (txtNgaySinh) { txtNgaySinh.value = normalizeDateValue(student.ngaySinh); txtNgaySinh.disabled = false; txtNgaySinh.style.backgroundColor = ""; }
        const errorSV = document.getElementById("errorSV");
        if (errorSV) errorSV.innerText = "";
        if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;
        showSinhVienForm();
"""
new_edit = """
        currentFormAction = "edit_sv";
        const student = dsSV[selectedStudentIndex];
        if (txtMaSV) {
            txtMaSV.value = student.maSV;
            txtMaSV.disabled = true;
            txtMaSV.style.backgroundColor = "#e5e7eb";
        }
        if (txtHoTen) { txtHoTen.value = student.hoTen; txtHoTen.disabled = false; txtHoTen.style.backgroundColor = ""; }
        if (txtNgaySinh) { txtNgaySinh.value = normalizeDateValue(student.ngaySinh); txtNgaySinh.disabled = false; txtNgaySinh.style.backgroundColor = ""; }
        if (formSinhVienTitle) formSinhVienTitle.innerText = "Hiệu chỉnh thông tin sinh viên";
        if (formSinhVienButtons) formSinhVienButtons.style.display = "flex";
        const errorSV = document.getElementById("errorSV");
        if (errorSV) errorSV.innerText = "";
        if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;
        showSinhVienForm();
"""
js = js.replace(old_edit, new_edit)

# Update btnDetailAdd
old_add = """
        currentFormAction = "add_sv";
        selectedStudentIndex = -1;
        clearStudentForm();
        renderSelectedStudentInfo(null);
        showSinhVienForm();
"""
new_add = """
        currentFormAction = "add_sv";
        selectedStudentIndex = -1;
        clearStudentForm();
        if (txtMaSV) { txtMaSV.disabled = false; txtMaSV.style.backgroundColor = ""; }
        if (txtHoTen) { txtHoTen.disabled = false; txtHoTen.style.backgroundColor = ""; }
        if (txtNgaySinh) { txtNgaySinh.disabled = false; txtNgaySinh.style.backgroundColor = ""; }
        if (formSinhVienTitle) formSinhVienTitle.innerText = "Thêm sinh viên mới";
        if (formSinhVienButtons) formSinhVienButtons.style.display = "flex";
        renderSelectedStudentInfo(null);
        showSinhVienForm();
"""
js = js.replace(old_add, new_add)

with open('static/js/sinhVien_v15.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v14\.js(\?v=\d+)?', 'sinhVien_v15.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully applied view mode patch.")

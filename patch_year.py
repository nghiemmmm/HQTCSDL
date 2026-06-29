import re

with open('static/js/sinhVien_v9.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

# 1. Update strict validation logic
old_validation = """
        const birthDate = new Date(student.ngaySinh);
        const currentDate = new Date();
        let age = currentDate.getFullYear() - birthDate.getFullYear();
        const m = currentDate.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && currentDate.getDate() < birthDate.getDate())) {
            age--;
        }
        if (age < 18) {
            alert("Sinh viên phải đủ 18 tuổi.");
            return;
        }
"""
new_validation = """
        const birthDate = new Date(student.ngaySinh);
        const currentDate = new Date();
        let age = currentDate.getFullYear() - birthDate.getFullYear();
        if (age < 18) {
            alert("Sinh viên phải đủ 18 tuổi (tính theo năm sinh).");
            return;
        }
"""
sv_js = sv_js.replace(old_validation.strip(), new_validation.strip())

# 2. Update max attribute logic
old_max_attr = """
if (typeof txtNgaySinh !== 'undefined' && txtNgaySinh) {
    const today = new Date();
    const maxYear = today.getFullYear() - 18;
    const maxMonth = String(today.getMonth() + 1).padStart(2, '0');
    const maxDay = String(today.getDate()).padStart(2, '0');
    txtNgaySinh.max = `${maxYear}-${maxMonth}-${maxDay}`;
}
"""
new_max_attr = """
if (typeof txtNgaySinh !== 'undefined' && txtNgaySinh) {
    const today = new Date();
    const maxYear = today.getFullYear() - 18;
    txtNgaySinh.max = `${maxYear}-12-31`;
}
"""
sv_js = sv_js.replace(old_max_attr.strip(), new_max_attr.strip())

with open('static/js/sinhVien_v10.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v9\.js(\?v=\d+)?', 'sinhVien_v10.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully applied year-only age patch.")

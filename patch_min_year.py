import re

with open('static/js/sinhVien_v12.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

# 1. Update strict validation logic to include max age (e.g., 100 years old)
old_validation = """
        const birthDate = new Date(student.ngaySinh);
        const currentDate = new Date();
        let age = currentDate.getFullYear() - birthDate.getFullYear();
        if (age < 18) {
            alert("Sinh viên phải đủ 18 tuổi (tính theo năm sinh).");
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
        if (age > 100) {
            alert("Sinh viên không được lớn hơn 100 tuổi hợp lý chút đi!");
            return;
        }
"""
sv_js = sv_js.replace(old_validation.strip(), new_validation.strip())

# 2. Update min attribute logic
old_max_attr = """
if (typeof txtNgaySinh !== 'undefined' && txtNgaySinh) {
    const today = new Date();
    const maxYear = today.getFullYear() - 18;
    txtNgaySinh.max = `${maxYear}-12-31`;
}
"""
new_max_attr = """
if (typeof txtNgaySinh !== 'undefined' && txtNgaySinh) {
    const today = new Date();
    const maxYear = today.getFullYear() - 18;
    const minYear = today.getFullYear() - 100;
    txtNgaySinh.max = `${maxYear}-12-31`;
    txtNgaySinh.min = `${minYear}-01-01`;
}
"""
sv_js = sv_js.replace(old_max_attr.strip(), new_max_attr.strip())

with open('static/js/sinhVien_v13.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v12\.js(\?v=\d+)?', 'sinhVien_v13.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully applied min year age patch.")

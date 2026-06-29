import re

with open('static/js/sinhVien_v8.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

append_js = """
// Set max attribute for Ngay Sinh to 18 years ago
if (typeof txtNgaySinh !== 'undefined' && txtNgaySinh) {
    const today = new Date();
    const maxYear = today.getFullYear() - 18;
    const maxMonth = String(today.getMonth() + 1).padStart(2, '0');
    const maxDay = String(today.getDate()).padStart(2, '0');
    txtNgaySinh.max = `${maxYear}-${maxMonth}-${maxDay}`;
}
"""

with open('static/js/sinhVien_v9.js', 'w', encoding='utf-8') as f:
    f.write(sv_js + append_js)


with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v8\.js(\?v=\d+)?', 'sinhVien_v9.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully applied max date patch.")

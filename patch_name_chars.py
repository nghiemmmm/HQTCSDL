import re

# 1. Update giaoVien_v3.js -> giaoVien_v4.js
with open('static/js/giaoVien_v3.js', 'r', encoding='utf-8') as f:
    gv_js = f.read()

gv_append = """
function blockNonLetters(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[\\p{L}\\s]+$/u.test(e.key)) {
        e.preventDefault();
    }
}
function sanitizeNameInput(e) {
    e.target.value = e.target.value.replace(/[^\\p{L}\\s]/gu, '');
}
if (hoGVInput) {
    hoGVInput.addEventListener('keydown', blockNonLetters);
    hoGVInput.addEventListener('input', sanitizeNameInput);
}
if (tenGVInput) {
    tenGVInput.addEventListener('keydown', blockNonLetters);
    tenGVInput.addEventListener('input', sanitizeNameInput);
}
"""
with open('static/js/giaoVien_v4.js', 'w', encoding='utf-8') as f:
    f.write(gv_js + gv_append)

# 2. Update sinhVien_v3.js -> sinhVien_v4.js
with open('static/js/sinhVien_v3.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

sv_append = """
function blockNonLetters(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[\\p{L}\\s]+$/u.test(e.key)) {
        e.preventDefault();
    }
}
function sanitizeNameInput(e) {
    e.target.value = e.target.value.replace(/[^\\p{L}\\s]/gu, '');
}
if (typeof txtHoTen !== 'undefined' && txtHoTen) {
    txtHoTen.addEventListener('keydown', blockNonLetters);
    txtHoTen.addEventListener('input', sanitizeNameInput);
}
"""
with open('static/js/sinhVien_v4.js', 'w', encoding='utf-8') as f:
    f.write(sv_js + sv_append)

# 3. Update HTML files to point to v4
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html_gv = f.read()
html_gv = re.sub(r'giaoVien_v3\.js(\?v=\d+)?', 'giaoVien_v4.js', html_gv)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html_gv)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v3\.js(\?v=\d+)?', 'sinhVien_v4.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully patched JS and HTML for Name fields.")

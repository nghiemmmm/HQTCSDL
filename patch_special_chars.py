import re

# 1. Update giaoVien_v2.js -> giaoVien_v3.js
with open('static/js/giaoVien_v2.js', 'r', encoding='utf-8') as f:
    gv_js = f.read()

gv_append = """
function blockSpecialChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[a-zA-Z0-9]+$/.test(e.key)) {
        e.preventDefault();
    }
}
function sanitizeInput(e) {
    e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
}
if (maGVInput) {
    maGVInput.addEventListener('keydown', blockSpecialChars);
    maGVInput.addEventListener('input', sanitizeInput);
}
"""
with open('static/js/giaoVien_v3.js', 'w', encoding='utf-8') as f:
    f.write(gv_js + gv_append)

# 2. Update sinhVien_v2.js -> sinhVien_v3.js
with open('static/js/sinhVien_v2.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

sv_append = """
function blockSpecialChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[a-zA-Z0-9]+$/.test(e.key)) {
        e.preventDefault();
    }
}
function sanitizeInput(e) {
    e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
}
if (typeof txtMaLop !== 'undefined' && txtMaLop) {
    txtMaLop.addEventListener('keydown', blockSpecialChars);
    txtMaLop.addEventListener('input', sanitizeInput);
}
if (typeof txtMaSV !== 'undefined' && txtMaSV) {
    txtMaSV.addEventListener('keydown', blockSpecialChars);
    txtMaSV.addEventListener('input', sanitizeInput);
}
"""
with open('static/js/sinhVien_v3.js', 'w', encoding='utf-8') as f:
    f.write(sv_js + sv_append)

# 3. Update HTML files to point to v3
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html_gv = f.read()
html_gv = re.sub(r'giaoVien_v2\.js(\?v=\d+)?', 'giaoVien_v3.js', html_gv)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html_gv)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v2\.js(\?v=\d+)?', 'sinhVien_v3.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully patched JS and HTML for special characters.")

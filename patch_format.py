import re

# 1. Update giaoVien_v4.js -> giaoVien_v5.js
with open('static/js/giaoVien_v4.js', 'r', encoding='utf-8') as f:
    gv_js = f.read()

gv_append = """
function forceUppercase(e) {
    const start = e.target.selectionStart;
    const end = e.target.selectionEnd;
    e.target.value = e.target.value.toUpperCase();
    e.target.setSelectionRange(start, end);
}

function formatNameOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/\\s+/g, ' ').trim();
    val = val.toLowerCase().replace(/(?:^|\\s)\\S/g, function(a) { return a.toUpperCase(); });
    e.target.value = val;
}

if (maGVInput) {
    maGVInput.addEventListener('input', forceUppercase);
}
if (hoGVInput) {
    hoGVInput.addEventListener('blur', formatNameOnBlur);
}
if (tenGVInput) {
    tenGVInput.addEventListener('blur', formatNameOnBlur);
}
"""
with open('static/js/giaoVien_v5.js', 'w', encoding='utf-8') as f:
    f.write(gv_js + gv_append)


# 2. Update sinhVien_v4.js -> sinhVien_v5.js
with open('static/js/sinhVien_v4.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

sv_append = """
function forceUppercase(e) {
    const start = e.target.selectionStart;
    const end = e.target.selectionEnd;
    e.target.value = e.target.value.toUpperCase();
    e.target.setSelectionRange(start, end);
}

function formatNameOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/\\s+/g, ' ').trim();
    val = val.toLowerCase().replace(/(?:^|\\s)\\S/g, function(a) { return a.toUpperCase(); });
    e.target.value = val;
}

function formatClassNameOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/\\s+/g, ' ').trim();
    e.target.value = val;
}

if (typeof txtMaLop !== 'undefined' && txtMaLop) {
    txtMaLop.addEventListener('input', forceUppercase);
}
if (typeof txtMaSV !== 'undefined' && txtMaSV) {
    txtMaSV.addEventListener('input', forceUppercase);
}
if (typeof txtHoTen !== 'undefined' && txtHoTen) {
    txtHoTen.addEventListener('blur', formatNameOnBlur);
}
if (typeof txtTenLop !== 'undefined' && txtTenLop) {
    txtTenLop.addEventListener('blur', formatClassNameOnBlur);
}
"""
with open('static/js/sinhVien_v5.js', 'w', encoding='utf-8') as f:
    f.write(sv_js + sv_append)


# 3. Update HTML files to point to v5
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html_gv = f.read()
html_gv = re.sub(r'giaoVien_v4\.js(\?v=\d+)?', 'giaoVien_v5.js', html_gv)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html_gv)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v4\.js(\?v=\d+)?', 'sinhVien_v5.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully patched JS and HTML for auto-formatting.")

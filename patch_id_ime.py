import re

format_id_on_blur = """
function formatIdOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/[^a-zA-Z0-9]/g, '');
    e.target.value = val.toUpperCase();
    
    // Trigger input event manually so that checkDuplicate gets the latest uppercase/sanitized value
    e.target.dispatchEvent(new Event('input'));
}
"""

# 1. Update sinhVien_v7.js -> sinhVien_v8.js
with open('static/js/sinhVien_v7.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

sv_js = re.sub(r'function blockSpecialChars\(e\) \{[\s\S]*?\}\s*function sanitizeInput\(e\) \{[\s\S]*?\}', '', sv_js)
sv_js = sv_js.replace("txtMaLop.addEventListener('keydown', blockSpecialChars);", "")
sv_js = sv_js.replace("txtMaLop.addEventListener('input', sanitizeInput);", "")
sv_js = sv_js.replace("txtMaSV.addEventListener('keydown', blockSpecialChars);", "")
sv_js = sv_js.replace("txtMaSV.addEventListener('input', sanitizeInput);", "")

sv_js = re.sub(r'function forceUppercase\(e\) \{[\s\S]*?\}', '', sv_js)
sv_js = sv_js.replace("txtMaLop.addEventListener('input', forceUppercase);", "txtMaLop.addEventListener('blur', formatIdOnBlur);")
sv_js = sv_js.replace("txtMaSV.addEventListener('input', forceUppercase);", "txtMaSV.addEventListener('blur', formatIdOnBlur);")

sv_js = sv_js + "\n" + format_id_on_blur

with open('static/js/sinhVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

# 2. Update giaoVien_v7.js -> giaoVien_v8.js
with open('static/js/giaoVien_v7.js', 'r', encoding='utf-8') as f:
    gv_js = f.read()

gv_js = re.sub(r'function blockSpecialChars\(e\) \{[\s\S]*?\}\s*function sanitizeInput\(e\) \{[\s\S]*?\}', '', gv_js)
gv_js = gv_js.replace("maGVInput.addEventListener('keydown', blockSpecialChars);", "")
gv_js = gv_js.replace("maGVInput.addEventListener('input', sanitizeInput);", "")

gv_js = re.sub(r'function forceUppercase\(e\) \{[\s\S]*?\}', '', gv_js)
gv_js = gv_js.replace("maGVInput.addEventListener('input', forceUppercase);", "maGVInput.addEventListener('blur', formatIdOnBlur);")

gv_js = gv_js + "\n" + format_id_on_blur

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(gv_js)

# 3. Update HTML files to point to v8
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html_gv = f.read()
html_gv = re.sub(r'giaoVien_v7\.js(\?v=\d+)?', 'giaoVien_v8.js', html_gv)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html_gv)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v7\.js(\?v=\d+)?', 'sinhVien_v8.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully patched JS for ID IME fix.")

import os
import shutil

# Restore v6
shutil.copy('static/js/sinhVien_v6.js', 'static/js/sinhVien_v7.js')
shutil.copy('static/js/giaoVien_v6.js', 'static/js/giaoVien_v7.js')

with open('static/js/sinhVien_v7.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

# Manually remove the exact strings
to_remove_sv = """
function blockNonLetters(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[\\p{L}\\s]+$/u.test(e.key)) {
        e.preventDefault();
    }
}
function sanitizeNameInput(e) {
    e.target.value = e.target.value.replace(/[^\\p{L}\\s]/gu, '');
}
"""
sv_js = sv_js.replace(to_remove_sv.strip(), "")
sv_js = sv_js.replace("txtHoTen.addEventListener('keydown', blockNonLetters);", "")
sv_js = sv_js.replace("txtHoTen.addEventListener('input', sanitizeNameInput);", "")

new_format_name = """function formatNameOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/[^\\p{L}\\s]/gu, '');
    val = val.replace(/\\s+/g, ' ').trim();
    val = val.toLowerCase().replace(/(?:^|\\s)\\S/g, function(a) { return a.toUpperCase(); });
    e.target.value = val;
}"""

# Replace formatNameOnBlur carefully by finding it
start_idx = sv_js.find('function formatNameOnBlur(e) {')
end_idx = sv_js.find('e.target.value = val;\n}', start_idx) + len('e.target.value = val;\n}')
if start_idx != -1 and end_idx != -1:
    sv_js = sv_js[:start_idx] + new_format_name + sv_js[end_idx:]

with open('static/js/sinhVien_v7.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

with open('static/js/giaoVien_v7.js', 'r', encoding='utf-8') as f:
    gv_js = f.read()

to_remove_gv = """
function blockNonLetters(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[\\p{L}\\s]+$/u.test(e.key)) {
        e.preventDefault();
    }
}
function sanitizeNameInput(e) {
    e.target.value = e.target.value.replace(/[^\\p{L}\\s]/gu, '');
}
"""
gv_js = gv_js.replace(to_remove_gv.strip(), "")
gv_js = gv_js.replace("hoGVInput.addEventListener('keydown', blockNonLetters);", "")
gv_js = gv_js.replace("hoGVInput.addEventListener('input', sanitizeNameInput);", "")
gv_js = gv_js.replace("tenGVInput.addEventListener('keydown', blockNonLetters);", "")
gv_js = gv_js.replace("tenGVInput.addEventListener('input', sanitizeNameInput);", "")

start_idx = gv_js.find('function formatNameOnBlur(e) {')
end_idx = gv_js.find('e.target.value = val;\n}', start_idx) + len('e.target.value = val;\n}')
if start_idx != -1 and end_idx != -1:
    gv_js = gv_js[:start_idx] + new_format_name + gv_js[end_idx:]

with open('static/js/giaoVien_v7.js', 'w', encoding='utf-8') as f:
    f.write(gv_js)

print("Fix applied.")

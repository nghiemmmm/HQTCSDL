import re

with open('static/js/sinhVien_v18.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the try-catch block in selectStudent
pattern = r'(try\s*\{\s*const\s*token\s*=\s*localStorage\.getItem\("token"\);\s*if\s*\(token\)\s*\{\s*const\s*res\s*=\s*await\s*fetch\([^;]+;\s*if\s*\(res\.ok\)\s*\{\s*const\s*status\s*=\s*await\s*res\.json\(\);\s*if\s*\(status\.da_thi\s*\|\|\s*status\.da_dang_ky\)\s*\{[^\}]+\}\s*\}\s*\}\s*\}\s*catch\s*\(e\)\s*\{\s*console\.error\([^)]+\);\s*\})'

repl = r"""try {
            const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`);
            if (res.ok) {
                const status = await res.json();
                if (status.da_thi || status.da_dang_ky) {
                    if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                    if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                }
            }
        } catch(e) { console.error("Error check status", e); }"""

js = re.sub(pattern, repl, js, flags=re.MULTILINE)

with open('static/js/sinhVien_v19.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v18\.js(\?v=\d+)?', 'sinhVien_v19.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched fetch without token requirement.")

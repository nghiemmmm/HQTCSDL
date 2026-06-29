import json
import re

with open('static/js/sinhVien_v17.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix the condition to check both da_thi and da_dang_ky
pattern = r'(if\s*\(\s*status\.da_thi\s*\)\s*\{)'
repl = r'if (status.da_thi || status.da_dang_ky) {'
js = re.sub(pattern, repl, js)

with open('static/js/sinhVien_v18.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v17\.js(\?v=\d+)?', 'sinhVien_v18.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched da_thi || da_dang_ky in selectStudent")

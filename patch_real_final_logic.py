import re

with open('static/js/sinhVien_v26.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the delete logic block using a robust regex
# Look for the start of the block: if (checkData.da_thi || checkData.da_dang_ky)
# And replace up to: return; }
pattern_delete = r'if\s*\(\s*checkData\.da_thi\s*\|\|\s*checkData\.da_dang_ky\s*\)\s*\{[\s\S]*?return;\s*\}'
repl_delete = r"""if (checkData.da_thi) {
                alert(`Sinh viên này đã thi. Không thể xóa!`);
                return;
            }"""

js = re.sub(pattern_delete, repl_delete, js)

with open('static/js/sinhVien_v27.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v26\.js(\?v=\d+)?', 'sinhVien_v27.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Real final logic applied to btnDetailDelete.")

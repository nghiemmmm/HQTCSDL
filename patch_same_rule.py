import re

with open('static/js/sinhVien_v23.js', 'r', encoding='utf-8') as f:
    js = f.read()

# I will just find the check block and combine the if statements for btnDetailEdit and btnDetailDelete
pattern = r'(if\s*\(\s*status\.da_thi\s*\|\|\s*status\.da_dang_ky\s*\)\s*\{\s*if\s*\(\s*btnDetailDelete\s*\)\s*\{\s*btnDetailDelete\.disabled[^}]+\}\s*\})\s*(if\s*\(\s*status\.da_thi\s*\)\s*\{\s*if\s*\(\s*btnDetailEdit\s*\)\s*\{\s*btnDetailEdit\.disabled[^}]+\}\s*\})'

# Actually, an easier way is to just replace the two ifs with one that applies to both
# Let's write it explicitly:

old_block = """                if (status.da_thi || status.da_dang_ky) {
                    if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                }
                if (status.da_thi) {
                    if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                }"""

new_block = """                if (status.da_thi || status.da_dang_ky) {
                    if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                    if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                }"""

js = js.replace(old_block, new_block)

# Also update the alert inside btnDetailEdit.onclick
old_alert_block = """            if (checkData.da_thi) {
                alert(`Sinh viên này đã thi. Không thể hiệu chỉnh!`);"""
new_alert_block = """            if (checkData.da_thi || checkData.da_dang_ky) {
                alert(`Sinh viên này đã tham gia hoặc đăng ký thi. Không thể hiệu chỉnh!`);"""

js = js.replace(old_alert_block, new_alert_block)

with open('static/js/sinhVien_v24.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v23\.js(\?v=\d+)?', 'sinhVien_v24.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied same rule for edit and delete.")

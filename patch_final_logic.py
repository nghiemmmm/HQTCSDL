import re

with open('static/js/sinhVien_v25.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update selectStudent dimming logic
old_dim_block = """                if (status.da_thi || status.da_dang_ky) {
                    if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                    if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                }"""

new_dim_block = """                if (status.da_thi) {
                    if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                    if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                }"""
js = js.replace(old_dim_block, new_dim_block)

# 2. Update btnDetailEdit.onclick
old_edit_alert = """            if (checkData.da_thi || checkData.da_dang_ky) {
                alert(`Sinh viên này đã thi hoặc thuộc lớp đang có lịch thi. Không thể hiệu chỉnh!`);
                return;
            }"""
new_edit_alert = """            if (checkData.da_thi) {
                alert(`Sinh viên này đã thi. Không thể hiệu chỉnh!`);
                return;
            }"""
js = js.replace(old_edit_alert, new_edit_alert)

# 3. Update btnDetailDelete.onclick
old_delete_logic = """            if (checkData.da_thi || checkData.da_dang_ky) {
                // Nếu sinh viên đã thi hoặc đã đăng ký, không cho xóa
                let errorMsg = "Sinh viên này ";
                if (checkData.da_thi && checkData.da_dang_ky) {
                    errorMsg += "đã thi và lớp đang có lịch thi";
                } else if (checkData.da_thi) {
                    errorMsg += "đã thi";
                } else {
                    errorMsg += "thuộc lớp đang có lịch thi";
                }
                alert(`${errorMsg}. Không thể xóa!`);
                return;
            }"""
new_delete_logic = """            if (checkData.da_thi) {
                alert(`Sinh viên này đã thi. Không thể xóa!`);
                return;
            }"""
js = js.replace(old_delete_logic, new_delete_logic)

with open('static/js/sinhVien_v26.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v25\.js(\?v=\d+)?', 'sinhVien_v26.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Final logic applied: ONLY block if da_thi is true.")

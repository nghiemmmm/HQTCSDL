import re

with open('static/js/sinhVien_v24.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Update alert in btnDetailDelete.onclick
old_delete_msg = """                if (checkData.da_thi && checkData.da_dang_ky) {
                    errorMsg += "đã thi và đã đăng ký thi";
                } else if (checkData.da_thi) {
                    errorMsg += "đã thi";
                } else {
                    errorMsg += "đã đăng ký thi";
                }"""

new_delete_msg = """                if (checkData.da_thi && checkData.da_dang_ky) {
                    errorMsg += "đã thi và lớp đang có lịch thi";
                } else if (checkData.da_thi) {
                    errorMsg += "đã thi";
                } else {
                    errorMsg += "thuộc lớp đang có lịch thi";
                }"""
js = js.replace(old_delete_msg, new_delete_msg)

# Update alert in btnDetailEdit.onclick
old_edit_alert = """alert(`Sinh viên này đã tham gia hoặc đăng ký thi. Không thể hiệu chỉnh!`);"""
new_edit_alert = """alert(`Sinh viên này đã thi hoặc thuộc lớp đang có lịch thi. Không thể hiệu chỉnh!`);"""
js = js.replace(old_edit_alert, new_edit_alert)

with open('static/js/sinhVien_v25.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v24\.js(\?v=\d+)?', 'sinhVien_v25.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated alert messages.")

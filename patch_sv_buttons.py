import re

# 1. Update formSinhVien.html
with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Hide Xoa and Hieu chinh initially
html = html.replace('<button id="btnDetailDelete" type="button" data-permission="delete_student">Xoa</button>',
                    '<button id="btnDetailDelete" type="button" data-permission="delete_student" style="display: none;">Xoa</button>')
html = html.replace('<button id="btnDetailEdit" type="button" data-permission="update_student">Hieu chinh</button>',
                    '<button id="btnDetailEdit" type="button" data-permission="update_student" style="display: none;">Hieu chinh</button>')

html = re.sub(r'sinhVien_v28\.js\?v=\d+', 'sinhVien_v28.js?v=7', html)

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update sinhVien_v28.js
with open('static/js/sinhVien_v28.js', 'r', encoding='utf-8') as f:
    js = f.read()

# In selectStudent, show the buttons
old_select = r'if \(btnDetailAdd\) btnDetailAdd\.style\.display = "none";\n\s*if \(btnDetailEdit\)'
new_select = 'if (btnDetailAdd) btnDetailAdd.style.display = "none";\n          if (btnDetailEdit) { btnDetailEdit.style.display = "inline-block"; }\n          if (btnDetailDelete) { btnDetailDelete.style.display = "inline-block"; }\n          if (btnDetailEdit)'
js = re.sub(old_select, new_select, js)

# In clearStudentForm, hide the buttons
old_clear = r'function clearStudentForm\(\) \{\n\s*if \(btnSVUndo\) btnSVUndo\.style\.display = "none";'
new_clear = 'function clearStudentForm() {\n      if (btnDetailEdit) btnDetailEdit.style.display = "none";\n      if (btnDetailDelete) btnDetailDelete.style.display = "none";\n      if (btnSVUndo) btnSVUndo.style.display = "none";'
js = re.sub(old_clear, new_clear, js)

with open('static/js/sinhVien_v28.js', 'w', encoding='utf-8') as f:
    f.write(js)

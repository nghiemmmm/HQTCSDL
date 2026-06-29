import re

with open('static/js/sinhVien_v21.js', 'r', encoding='utf-8') as f:
    js = f.read()

# The first one is in my try block, the second one is below currentFormAction
pattern = r'(currentFormAction\s*=\s*"edit_sv";\s*)(const\s*student\s*=\s*dsSV\[selectedStudentIndex\];)'
repl = r'\1/* \2 removed to avoid redeclaration */'
js = re.sub(pattern, repl, js)

with open('static/js/sinhVien_v22.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v21\.js(\?v=\d+)?', 'sinhVien_v22.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Syntax error patched.")

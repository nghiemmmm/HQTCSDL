import re

# 1. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add SDT validation
old_sdt_check = r'if \(obj\.sodtll\.length > 15\) return showError\("S\?`\s*\?\`i\?n tho\?i t\?`i \?\`a 15 k\?\? t\?\!"\);'

# If regex for exact string fails, we'll just insert after it.
# Let's use a simpler replace by finding the line containing sodtll.length
def insert_sdt_validation(match):
    return match.group(0) + '\n    if (obj.sodtll && !/^[0-9]+$/.test(obj.sodtll)) return showError("Số điện thoại chỉ được chứa các chữ số (0-9)!");\n    if (obj.sodtll && obj.sodtll.length < 10) return showError("Số điện thoại không hợp lệ (tối thiểu 10 số)!");'

js = re.sub(r'if \(obj\.sodtll\.length > 15\) return showError\([^)]+\);', insert_sdt_validation, js)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formGiaoVien.html
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=14', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

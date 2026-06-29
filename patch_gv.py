import re

# 1. Update formGiaoVien.html
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace block page_title
html = re.sub(r'{%\s*block\s+page_title\s*%}Giao vien{%\s*endblock\s*%}', '{% block page_title %}Quan ly giao vien{% endblock %}', html)

# Remove <h2>QUAN LY GIAO VIEN</h2>
html = re.sub(r'<h2>QUAN LY GIAO VIEN</h2>', '', html)

# Add id and hide form-grid
html = re.sub(r'<div class="form-grid">', '<div class="form-grid" id="formGrid" style="display: none;">', html)

html = re.sub(r'giaoVien\.css\?v=\d+', 'giaoVien.css?v=3', html)
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=9', html)

with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 2. Update giaoVien.css
with open('static/css/giaoVien.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Remove max-width: 850px from .wrap
css = re.sub(r'\.wrap\s*\{[^}]*max-width:\s*850px;[^}]*\}', lambda m: m.group(0).replace('max-width: 850px;', 'width: 100%;'), css)

with open('static/css/giaoVien.css', 'w', encoding='utf-8') as f:
    f.write(css)


# 3. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add display: grid on them()
js = js.replace('function them() {', 'function them() {\n    const fg = document.getElementById("formGrid");\n    if (fg) fg.style.display = "grid";')

# Add display: grid on sua()
js = js.replace('function sua() {', 'function sua() {\n    const fg = document.getElementById("formGrid");\n    if (fg) fg.style.display = "grid";')

# Add display: none on huy()
js = js.replace('function huy() {', 'function huy() {\n    const fg = document.getElementById("formGrid");\n    if (fg) fg.style.display = "none";')

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

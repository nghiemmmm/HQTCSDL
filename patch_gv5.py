import re

# 1. Update giaoVien.css
with open('static/css/giaoVien.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Add justify-content: flex-end to .toolbar
old_toolbar = r'\.toolbar\s*\{\s*display:\s*flex;\s*flex-wrap:\s*wrap;'
new_toolbar = '.toolbar {\n    display: flex;\n    justify-content: flex-end;\n    flex-wrap: wrap;'
css = re.sub(old_toolbar, new_toolbar, css)

with open('static/css/giaoVien.css', 'w', encoding='utf-8') as f:
    f.write(css)


# 2. Update formGiaoVien.html
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove margin-left: auto from btnThem
html = html.replace('margin-left: auto; ', '')
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=13', html)
html = re.sub(r'giaoVien\.css\?v=\d+', 'giaoVien.css?v=4', html)

with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 3. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Update setButtonState("selected") to show btnHuy
old_state = r'\} else if \(state === "selected"\) \{\n\s*if \(btnThem\) btnThem\.style\.display = "none";\n\s*if \(btnSua\) btnSua\.style\.display = "inline-block";\n\s*if \(btnXoa\) btnXoa\.style\.display = "inline-block";\n\s*if \(btnUndo\) btnUndo\.style\.display = stackUndo\.length > 0 \? "inline-block" : "none";\n\s*if \(btnGhi\) btnGhi\.style\.display = "none";\n\s*if \(btnHuy\) btnHuy\.style\.display = "none";'

new_state = """} else if (state === "selected") {
    if (btnThem) btnThem.style.display = "none";
    if (btnSua) btnSua.style.display = "inline-block";
    if (btnXoa) btnXoa.style.display = "inline-block";
    if (btnUndo) btnUndo.style.display = stackUndo.length > 0 ? "inline-block" : "none";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "inline-block";"""

js = re.sub(old_state, new_state, js)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

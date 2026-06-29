import re

with open('static/css/monHoc.css', 'a', encoding='utf-8') as f:
    f.write("\n\n/* OVERRIDE */\n.toolbar {\n    justify-content: flex-end !important;\n    width: 100%;\n}\n")

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Bump CSS version again
html = re.sub(r'monHoc\.css\?v=\d+', 'monHoc.css?v=6', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Toolbar flex-end applied at EOF.")

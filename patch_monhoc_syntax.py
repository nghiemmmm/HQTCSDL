import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix syntax error caused by leftover code
garbage = """}
  return "MH" + String(max + 1).padStart(3, '0');
}"""
js = js.replace(garbage, "")

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Bump version to force reload
html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=14', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

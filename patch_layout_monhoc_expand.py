import re

# 1. Update HTML
with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update errorText
html = html.replace('margin-top:10px;', 'margin-top:5px; margin-bottom:5px;')
html = html.replace('min-height:20px;', '')

# Update action-bar
html = html.replace('margin: 15px 0;', 'margin-bottom: 15px;')
html = html.replace('flex-wrap: wrap;', '')

# Bump CSS version
html = re.sub(r'monHoc\.css\?v=\d+', 'monHoc.css?v=8', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update CSS
with open('static/css/monHoc.css', 'a', encoding='utf-8') as f:
    f.write("\n\n/* EXPAND WRAP WIDTH */\n.wrap {\n    max-width: 100% !important;\n}\n")

print("UI optimized: expanded width, aligned items to same row, and reduced margins.")

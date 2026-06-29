import re

# 1. Update HTML
with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove stateText div
html = re.sub(r'<!-- STATE -->\s*<div id="stateText"></div>', '', html)

# Bump CSS version
html = re.sub(r'monHoc\.css\?v=\d+', 'monHoc.css?v=5', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update CSS
with open('static/css/monHoc.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Add flex-end to toolbar
css = css.replace('.toolbar {\n    display: flex;', '.toolbar {\n    display: flex;\n    justify-content: flex-end;')

# Add btnThem specific styling
new_css = """
#btnThem {
    background-color: #0f766e;
    color: white;
    padding: 8px 16px;
    font-weight: 600;
    border-radius: 6px;
    border: none;
    font-size: 14px;
    transition: background-color 0.2s;
}
#btnThem:hover {
    background-color: #0d9488;
}
"""
css += new_css

with open('static/css/monHoc.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Removed state text and updated toolbar/btnThem styles.")

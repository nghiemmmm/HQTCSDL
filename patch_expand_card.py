import re

with open('static/css/sinhVien.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace width and margin in .page-wrap
# Find .page-wrap { ... width: min(1100px, 94vw); margin: 40px auto; ... }
old_width_margin = r'width:\s*min\(1100px,\s*94vw\);\s*margin:\s*40px\s*auto;'
new_width_margin = 'width: 100%;\\n      margin: 0 auto;\\n      padding: 20px;'

css = re.sub(old_width_margin, new_width_margin, css)

# There's also a media query for max-width: 640px
# .page-wrap { width: min(94vw, 560px); margin: 20px auto 28px; gap: 14px; }
old_mobile = r'width:\s*min\(94vw,\s*560px\);\s*margin:\s*20px\s*auto\s*28px;'
new_mobile = 'width: 100%;\\n          margin: 10px auto;\\n          padding: 0 10px;'
css = re.sub(old_mobile, new_mobile, css)

with open('static/css/sinhVien.css', 'w', encoding='utf-8') as f:
    f.write(css)

# Bump version in HTML templates
templates = ['templates/formSinhVien.html']
for t in templates:
    try:
        with open(t, 'r', encoding='utf-8') as f:
            html = f.read()
        html = re.sub(r'sinhVien\.css\?v=\d+', 'sinhVien.css?v=12', html)
        with open(t, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Bumped {t}")
    except Exception as e:
        print(f"Error {e}")

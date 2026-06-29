import re

with open('static/js/sinhVien_v28.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the text assignment with style.display = "none"
pattern = r'if\s*\(classFilterSummary\)\s*\{[\s\S]*?classFilterSummary\.textContent\s*=\s*keyword[\s\S]*?\?.*?[\s\S]*?:.*?;[\s\S]*?\}'
replacement = """if (classFilterSummary) {
        classFilterSummary.style.display = "none";
    }"""

js = re.sub(pattern, replacement, js)

with open('static/js/sinhVien_v28.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'sinhVien_v28\.js\?v=2', 'sinhVien_v28.js?v=3', html)

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

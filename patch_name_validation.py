import re

# 1. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add real-time input event listeners for Ho and Ten
name_validation = """
if (hoGVInput) {
    hoGVInput.addEventListener("input", function() {
        this.value = this.value.replace(/[^\\p{L}\\s]/gu, '');
    });
}
if (tenGVInput) {
    tenGVInput.addEventListener("input", function() {
        this.value = this.value.replace(/[^\\p{L}\\s]/gu, '');
    });
}
"""

js += name_validation

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formGiaoVien.html to bump JS version
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=16', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

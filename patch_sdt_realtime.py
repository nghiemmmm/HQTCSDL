import re

# 1. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add input event listener for SDT to block non-numeric characters
realtime_sdt_validation = """
if (sdtGVInput) {
    sdtGVInput.addEventListener("input", function() {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
}
"""

js += realtime_sdt_validation

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formGiaoVien.html to bump JS version
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=15', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

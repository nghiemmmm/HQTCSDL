import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Use regex to find the maMHInput block in window.them and replace it
# Pattern to match:
#     if(maMHInput) {
#         maMHInput.disabled = true;
#         maMHInput.style.backgroundColor = "#e5e7eb";
#         maMHInput.value = generateNextMaMH();
#     }
pattern = r'if\s*\(maMHInput\)\s*\{[^}]*maMHInput\.disabled\s*=\s*true;[^}]*maMHInput\.value\s*=\s*generateNextMaMH\(\);[^}]*\}'

replacement = """if(maMHInput) {
        maMHInput.disabled = false;
        maMHInput.style.backgroundColor = "";
        maMHInput.value = "";
        maMHInput.focus();
    }"""

js = re.sub(pattern, replacement, js)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=16', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

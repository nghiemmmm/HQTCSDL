import re

files_to_patch = [
    'static/js/monHoc.js',
    'static/js/giaoVien_v8.js',
    'static/js/sinhVien_v28.js',
    'static/js/lop.js'
]

new_show_error = """function showError(msg) {
  if (errorText) {
    errorText.style.color = "#dc2626";
    errorText.innerText = msg;
    if (window.messageTimeout) clearTimeout(window.messageTimeout);
    window.messageTimeout = setTimeout(() => {
      if (errorText.innerText === msg) errorText.innerText = "";
    }, 5000);
  }
}"""

new_show_success = """function showSuccess(msg) {
  if (errorText) {
    errorText.style.color = "#16a34a";
    errorText.innerText = msg;
    if (window.messageTimeout) clearTimeout(window.messageTimeout);
    window.messageTimeout = setTimeout(() => {
      if (errorText.innerText === msg) errorText.innerText = "";
    }, 5000);
  }
}"""

for file_path in files_to_patch:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            js = f.read()
        
        # Replace showError
        js = re.sub(r'function\s+showError\s*\([^)]*\)\s*\{[\s\S]*?(?=\nfunction|\n//)', new_show_error, js, count=1)
        
        # Replace showSuccess
        js = re.sub(r'function\s+showSuccess\s*\([^)]*\)\s*\{[\s\S]*?(?=\nfunction|\n//)', new_show_success, js, count=1)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(js)
        print(f"Patched {file_path}")
    except Exception as e:
        print(f"Failed to patch {file_path}: {e}")

# Bump version in templates
templates = ['templates/formMonHoc.html', 'templates/formGiaoVien.html', 'templates/formSinhVien.html']
for t in templates:
    try:
        with open(t, 'r', encoding='utf-8') as f:
            html = f.read()
        html = re.sub(r'monHoc\.js\?v=22', 'monHoc.js?v=23', html)
        html = re.sub(r'giaoVien_v8\.js', 'giaoVien_v8.js?v=2', html)
        html = re.sub(r'sinhVien_v28\.js', 'sinhVien_v28.js?v=2', html)
        with open(t, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Bumped version in {t}")
    except Exception as e:
        print(f"Failed to bump {t}: {e}")

import re

with open('static/js/sinhVien_v19.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the try-catch block in checkDuplicateSV
pattern = r'(try\s*\{\s*const\s*token\s*=\s*localStorage\.getItem\("token"\);\s*const\s*res\s*=\s*await\s*fetch\([^,]+,\s*\{\s*method:\s*\'GET\',\s*headers:\s*\{\s*\'Authorization\':\s*`Bearer\s*\$\{token\}`\s*\}\s*\}\);\s*if\s*\(res\.ok\)\s*\{\s*exists\s*=\s*true;\s*\}\s*\}\s*catch\s*\(e\)\s*\{\s*console\.error\([^)]+\);\s*\})'

repl = r"""try {
                      const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(val)}/check-status`);
                      if (res.ok) {
                          exists = true;
                      }
                  } catch (e) {
                      console.error("Duplicate check error:", e);
                  }"""

js = re.sub(pattern, repl, js, flags=re.MULTILINE)

with open('static/js/sinhVien_v20.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v19\.js(\?v=\d+)?', 'sinhVien_v20.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched duplicate check fetch without token.")

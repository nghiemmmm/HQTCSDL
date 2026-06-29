import re

with open('static/js/sinhVien_v11.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

old_fetch = "const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(val)}/check-status`);"
new_fetch = """
                    const token = localStorage.getItem("token");
                    const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(val)}/check-status`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
"""

sv_js = sv_js.replace(old_fetch, new_fetch.strip())

with open('static/js/sinhVien_v12.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v11\.js(\?v=\d+)?', 'sinhVien_v12.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully patched fetch with auth token.")

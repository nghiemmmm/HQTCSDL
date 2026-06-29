import re

with open('static/js/sinhVien_v20.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix selectStudent token block
old_select_block = """          try {
              const token = localStorage.getItem("token");
              if (token) {
                  const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`, 
{
                      headers: { 'Authorization': `Bearer ${token}` }
                  });
                  if (res.ok) {
                      const status = await res.json();
                      if (status.da_thi || status.da_dang_ky) {
                          if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; 
btnDetailEdit.style.cursor = "not-allowed"; }
                          if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = 
"0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                      }
                  }
              }
          } catch(e) { console.error("Error check status", e); }"""

# But because of whitespace differences, it's safer to use regex that ignores spaces inside the try block
pattern_try = r'try\s*\{\s*const\s*token\s*=\s*localStorage\.getItem\("token"\);\s*if\s*\(token\)\s*\{[\s\S]*?catch\(e\)\s*\{\s*console\.error\("Error check status",\s*e\);\s*\}'
repl_try = r"""try {
            const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`);
            if (res.ok) {
                const status = await res.json();
                if (status.da_thi || status.da_dang_ky) {
                    if (btnDetailDelete) { btnDetailDelete.disabled = true; btnDetailDelete.style.opacity = "0.4"; btnDetailDelete.style.cursor = "not-allowed"; }
                }
                if (status.da_thi) {
                    if (btnDetailEdit) { btnDetailEdit.disabled = true; btnDetailEdit.style.opacity = "0.4"; btnDetailEdit.style.cursor = "not-allowed"; }
                }
            }
        } catch(e) { console.error("Error check status", e); }"""

js = re.sub(pattern_try, repl_try, js)

# Also add check in btnDetailEdit
pattern_edit_btn = r'(if\s*\(\s*selectedStudentIndex\s*<\s*0\s*\|\|\s*!dsSV\[selectedStudentIndex\]\)\s*\{\s*alert\("Vui l[^"]+"\);\s*return;\s*\})'
repl_edit_btn = r"""\1
        
        const student = dsSV[selectedStudentIndex];
        try {
            const checkResponse = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(student.maSV)}/check-status`);
            const checkData = await checkResponse.json();
            if (checkData.da_thi) {
                alert(`Sinh viên này đã thi. Không thể hiệu chỉnh!`);
                return;
            }
        } catch(e) { console.error(e); }
"""
js = re.sub(pattern_edit_btn, repl_edit_btn, js)

# Make btnDetailEdit async
js = js.replace('btnDetailEdit.onclick = () => {', 'btnDetailEdit.onclick = async () => {')

with open('static/js/sinhVien_v21.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v20\.js(\?v=\d+)?', 'sinhVien_v21.js', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched v21 correctly.")

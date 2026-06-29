import re

# 1. Update backend service
with open('services/subject_service.py', 'r', encoding='utf-8') as f:
    svc = f.read()

# The block to remove:
old_svc_gen = """    max_mh = db.query(func.max(DbMonHoc.mamh)).scalar()
    if not max_mh:
        next_id = 1
    else:
        try:
            num = int(max_mh.strip()[2:])
            next_id = num + 1
        except ValueError:
            next_id = 1
            
    request.mamh = f"MH{str(next_id).zfill(3)}"
    """

# Replace with nothing (just rely on request.mamh provided by frontend)
# Wait, actually let's ensure request.mamh is stripped and uppercase, just in case
new_svc_gen = """    if not request.mamh:
        raise ConflictError("Mã môn học không được để trống")
    request.mamh = request.mamh.strip().upper()
"""

# Let's use regex to replace it
svc = re.sub(r'\s*max_mh = db\.query\(func\.max\(DbMonHoc\.mamh\)\)\.scalar\(\).*?request\.mamh = f"MH\{str\(next_id\)\.zfill\(3\)\}"\s*', new_svc_gen, svc, flags=re.DOTALL)

with open('services/subject_service.py', 'w', encoding='utf-8') as f:
    f.write(svc)

# 2. Update frontend js
with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Remove generateNextMaMH
js = re.sub(r'function generateNextMaMH\(\) \{.*?\}\s*\n*', '', js, flags=re.DOTALL)

# Update validate
old_val = """function validate() {
  var ten = tenMHInput ? tenMHInput.value.trim() : "";

  if (!ten) {"""
new_val = """function validate() {
  var ma = maMHInput ? maMHInput.value.trim() : "";
  var ten = tenMHInput ? tenMHInput.value.trim() : "";

  if (isThem && !ma) {
    showError("Vui lòng nhập Mã môn học.");
    return false;
  }
  if (!ten) {"""
js = js.replace(old_val, new_val)

# Update window.them
old_them = """    if(maMHInput) {
        maMHInput.disabled = true;
        maMHInput.style.backgroundColor = "#e5e7eb";
        maMHInput.value = generateNextMaMH();
    }"""
new_them = """    if(maMHInput) {
        maMHInput.disabled = false;
        maMHInput.style.backgroundColor = "";
        maMHInput.value = "";
        maMHInput.focus();
    }"""
js = js.replace(old_them, new_them)

# Update window.ghi
old_ghi = """  var obj = {
    tenmh: tenMHInput.value.trim()
  };
  
  if (isSua) {
      obj.mamh = maMHInput.value.trim();
  }"""
new_ghi = """  var obj = {
    mamh: maMHInput.value.trim(),
    tenmh: tenMHInput.value.trim()
  };"""
js = js.replace(old_ghi, new_ghi)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

# Bump CSS/JS version
with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=13', html)
with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Removed auto increment for subject code.")

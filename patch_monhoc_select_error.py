import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# I want to replace the block inside selectRow:
old_select_block = """          if (checkData.da_dangky_thi || checkData.da_thi) {
              if (btnSua) { btnSua.disabled = true; btnSua.style.opacity = "0.4"; btnSua.style.cursor = "not-allowed"; }
              if (btnXoa) { btnXoa.disabled = true; btnXoa.style.opacity = "0.4"; btnXoa.style.cursor = "not-allowed"; }
              
              let errorMsg = "Môn học này đã được đăng ký thi. Không thể sửa/xóa!";
              showError(errorMsg);
          }"""

new_select_block = """          if (checkData.da_dangky_thi || checkData.da_thi) {
              if (btnSua) { btnSua.disabled = false; btnSua.style.opacity = "0.4"; btnSua.style.cursor = "pointer"; }
              if (btnXoa) { btnXoa.disabled = false; btnXoa.style.opacity = "0.4"; btnXoa.style.cursor = "pointer"; }
          }"""

js = js.replace(old_select_block, new_select_block)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update script version
html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=11', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Removed error message from selectRow and kept buttons clickable.")

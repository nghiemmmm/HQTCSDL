import re

# 1. Patch formGiaoVien.html
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Initially hide Sua, Xoa, Undo
html = html.replace('<button id="btnSua" onclick="sua()" data-permission="update_teacher">Sua</button>',
                    '<button id="btnSua" onclick="sua()" data-permission="update_teacher" style="display: none;">Sua</button>')
html = html.replace('<button id="btnXoa" onclick="xoa()" data-permission="delete_teacher">Xoa</button>',
                    '<button id="btnXoa" onclick="xoa()" data-permission="delete_teacher" style="display: none;">Xoa</button>')
html = html.replace('<button id="btnUndo" onclick="undo()" data-any-permission="create_teacher,update_teacher,delete_teacher">Undo</button>',
                    '<button id="btnUndo" onclick="undo()" data-any-permission="create_teacher,update_teacher,delete_teacher" style="display: none; background: #6b7280; color: white;">Undo</button>')

html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=10', html)

with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 2. Patch giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace setButtonState
old_set_btn = """function setButtonState(state) {
  if (state === "default") {
    if (btnThem) btnThem.style.display = "inline-block";
    if (btnSua) btnSua.style.display = "inline-block";
    if (btnXoa) btnXoa.style.display = "inline-block";
    if (btnUndo) btnUndo.style.display = "inline-block";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "none";
  } else if (state === "editing") {
    if (btnThem) btnThem.style.display = "none";
    if (btnSua) btnSua.style.display = "none";
    if (btnXoa) btnXoa.style.display = "none";
    if (btnUndo) btnUndo.style.display = "none";
    if (btnGhi) btnGhi.style.display = "inline-block";
    if (btnHuy) btnHuy.style.display = "inline-block";
  }
}"""

# Fallback regex if verbatim match fails
js = re.sub(r'function setButtonState\(state\)\s*\{[\s\S]*?\}\s*\}', '', js)

new_set_btn = """function setButtonState(state) {
  if (state === "default") {
    if (btnThem) btnThem.style.display = "inline-block";
    if (btnSua) btnSua.style.display = "none";
    if (btnXoa) btnXoa.style.display = "none";
    if (btnUndo) btnUndo.style.display = stackUndo.length > 0 ? "inline-block" : "none";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "none";
  } else if (state === "selected") {
    if (btnThem) btnThem.style.display = "inline-block";
    if (btnSua) btnSua.style.display = "inline-block";
    if (btnXoa) btnXoa.style.display = "inline-block";
    if (btnUndo) btnUndo.style.display = stackUndo.length > 0 ? "inline-block" : "none";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "none";
  } else if (state === "editing") {
    if (btnThem) btnThem.style.display = "none";
    if (btnSua) btnSua.style.display = "none";
    if (btnXoa) btnXoa.style.display = "none";
    if (btnUndo) btnUndo.style.display = "none";
    if (btnGhi) btnGhi.style.display = "inline-block";
    if (btnHuy) btnHuy.style.display = "inline-block";
  }
}
"""

js = new_set_btn + js

# Update selectRow to check-status
old_selectRow = r'function selectRow\(index\) \{[\s\S]*?render\(\);\s*\}'
new_selectRow = """async function selectRow(index) {
  if (isSua || isThem) {
    showError("Vui lòng Ghi hoặc Hủy trước khi chọn giáo viên khác!");
    return;
  }
  clearError();

  selectedIndex = index;
  maGVInput.value = data[index].magv;
  hoGVInput.value = data[index].ho;
  tenGVInput.value = data[index].ten;
  diaChiGVInput.value = data[index].diachi;
  sdtGVInput.value = data[index].sodtll;

  setButtonState("selected");
  if (btnSua) { btnSua.disabled = false; btnSua.style.opacity = 1; btnSua.title = ""; }
  if (btnXoa) { btnXoa.disabled = false; btnXoa.style.opacity = 1; btnXoa.title = ""; }

  try {
    const res = await fetch(`/giaovien/${data[index].magv}/check-status`);
    const checkData = await res.json();
    if (checkData.co_gan_mon || checkData.co_cauhoi || checkData.da_thi) {
      if (btnSua) { btnSua.disabled = true; btnSua.style.opacity = 0.5; btnSua.title = "Giáo viên đã mở lớp thi, không thể sửa"; }
      if (btnXoa) { btnXoa.disabled = true; btnXoa.style.opacity = 0.5; btnXoa.title = "Giáo viên đã mở lớp thi, không thể xóa"; }
    }
  } catch (e) { console.error(e); }

  render();
}"""
js = re.sub(old_selectRow, new_selectRow, js)

# Update undo()
js = js.replace('async function undo() {\n  clearError();\n  if (stackUndo.length === 0)',
"""async function undo() {
  clearError();
  if (isSua) {
      if (selectedIndex >= 0 && data[selectedIndex]) {
          const gv = data[selectedIndex];
          hoGVInput.value = gv.ho;
          tenGVInput.value = gv.ten;
          diaChiGVInput.value = gv.diachi;
          sdtGVInput.value = gv.sodtll;
          if (btnUndo) btnUndo.style.display = "none";
      }
      return;
  }
  if (stackUndo.length === 0)""")

# Add checkGVUndo event listeners
undo_logic = """
function checkGVUndo() {
  if (isSua && selectedIndex >= 0 && data[selectedIndex]) {
    const gv = data[selectedIndex];
    const isHoChanged = hoGVInput.value.trim() !== (gv.ho || "").trim();
    const isTenChanged = tenGVInput.value.trim() !== (gv.ten || "").trim();
    const isDiaChiChanged = diaChiGVInput.value.trim() !== (gv.diachi || "").trim();
    const isSdtChanged = sdtGVInput.value.trim() !== (gv.sodtll || "").trim();
    
    if (isHoChanged || isTenChanged || isDiaChiChanged || isSdtChanged) {
      if (btnUndo) btnUndo.style.display = "inline-block";
    } else {
      if (btnUndo) btnUndo.style.display = "none";
    }
  }
}
if (hoGVInput) hoGVInput.addEventListener("input", checkGVUndo);
if (tenGVInput) tenGVInput.addEventListener("input", checkGVUndo);
if (diaChiGVInput) diaChiGVInput.addEventListener("input", checkGVUndo);
if (sdtGVInput) sdtGVInput.addEventListener("input", checkGVUndo);
"""
js += undo_logic

# Also fix the initial load of page to hide undo if stack is 0
js = js.replace('loadData();', 'loadData();\nsetButtonState("default");')

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

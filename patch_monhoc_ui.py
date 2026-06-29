import re

# 1. Update formMonHoc.html
with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add id and display:none to form-grid
html = html.replace('<div class="form-grid">', '<div class="form-grid" id="formGrid" style="display:none;">')

# Update script version
html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=9', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update monHoc.js
with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add var formGrid
js = js.replace('var errorText = document.getElementById("errorText");', 
                'var errorText = document.getElementById("errorText");\nvar formGrid = document.getElementById("formGrid");')

# Update setButtonState
old_setButtonState = """function setButtonState(state) {
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

new_setButtonState = """function setButtonState(state) {
  var showUndo = stackUndo.length > 0 ? "inline-block" : "none";
  
  if (state === "initial") {
    if (btnThem) btnThem.style.display = "inline-block";
    if (btnSua) btnSua.style.display = "none";
    if (btnXoa) btnXoa.style.display = "none";
    if (btnUndo) btnUndo.style.display = showUndo;
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "none";
  } else if (state === "default") {
    if (btnThem) btnThem.style.display = "inline-block";
    if (btnSua) btnSua.style.display = "inline-block";
    if (btnXoa) btnXoa.style.display = "inline-block";
    if (btnUndo) btnUndo.style.display = showUndo;
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
js = js.replace(old_setButtonState, new_setButtonState)

# Call setButtonState("initial") after data fetch
js = js.replace('setState(`Đã load ${data.length} môn học`);', 'setState(`Đã load ${data.length} môn học`);\n  setButtonState("initial");', 1)

# Update selectRow
js = js.replace('setState("Đang chọn: " + data[index].maMH);\n  render();', 
                'setState("Đang chọn: " + data[index].maMH);\n  if (formGrid) formGrid.style.display = "grid";\n  setButtonState("default");\n  render();')

# Update them()
js = js.replace('setButtonState("editing");', 'setButtonState("editing");\n  if (formGrid) formGrid.style.display = "grid";', 1)

# Update ghi() end
old_ghi_end = """  selectedIndex = -1;
  setButtonState("default");

  render();"""
new_ghi_end = """  selectedIndex = -1;
  if (formGrid) formGrid.style.display = "none";
  setButtonState("initial");

  render();"""
js = js.replace(old_ghi_end, new_ghi_end)

# Update thucHienXoa
old_xoa_end = """    selectedIndex = -1;
    clearError();
    showSuccess(resData.message);

    render();"""
new_xoa_end = """    selectedIndex = -1;
    clearError();
    showSuccess(resData.message);
    if (formGrid) formGrid.style.display = "none";
    setButtonState("initial");

    render();"""
js = js.replace(old_xoa_end, new_xoa_end)

# Update huy()
old_huy_end = """  selectedIndex = -1;
  setButtonState("default");
  render();"""
new_huy_end = """  selectedIndex = -1;
  if (formGrid) formGrid.style.display = "none";
  setButtonState("initial");
  render();"""
js = js.replace(old_huy_end, new_huy_end)

# Update undo() end to refresh initial state
old_undo_end = """    render();

  } catch (err) {"""
new_undo_end = """    if (selectedIndex === -1) setButtonState("initial");
    else setButtonState("default");
    render();

  } catch (err) {"""
js = js.replace(old_undo_end, new_undo_end)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("UI state patched.")

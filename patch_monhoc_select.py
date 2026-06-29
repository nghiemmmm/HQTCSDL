import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update setButtonState to reset disabled state and add "selected"
old_setButtonState = """function setButtonState(state) {
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

new_setButtonState = """function setButtonState(state) {
  var showUndo = stackUndo.length > 0 ? "inline-block" : "none";
  
  // Reset opacity/disabled
  if (btnSua) { btnSua.disabled = false; btnSua.style.opacity = "1"; btnSua.style.cursor = "pointer"; }
  if (btnXoa) { btnXoa.disabled = false; btnXoa.style.opacity = "1"; btnXoa.style.cursor = "pointer"; }
  
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
  } else if (state === "selected") {
    if (btnThem) btnThem.style.display = "none";
    if (btnSua) btnSua.style.display = "inline-block";
    if (btnXoa) btnXoa.style.display = "inline-block";
    if (btnUndo) btnUndo.style.display = "none";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "inline-block";
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


# 2. Update selectRow to be async and apply new logic
old_selectRow = """window.selectRow = function(index) {
  if (isSua || isThem) {
    showError("Vui lòng Ghi hoặc Hủy trước khi chọn môn khác!");
    return;
  }
  clearError();

  selectedIndex = index;
  if (maMHInput) maMHInput.value = data[index].maMH;
  if (tenMHInput) tenMHInput.value = data[index].tenMH;

  setState("Đang chọn: " + data[index].maMH);
  if (formGrid) formGrid.style.display = "grid";
  setButtonState("default");
  render();
};"""

new_selectRow = """window.selectRow = async function(index) {
  if (isSua || isThem) {
    showError("Vui lòng Ghi hoặc Hủy trước khi chọn môn khác!");
    return;
  }
  clearError();

  selectedIndex = index;
  var item = data[index];
  if (maMHInput) maMHInput.value = item.maMH;
  if (tenMHInput) tenMHInput.value = item.tenMH;

  setState("Đang chọn: " + item.maMH);
  if (formGrid) formGrid.style.display = "grid";
  setButtonState("selected");
  
  try {
      var checkRes = await fetch(`/monhoc/${encodeURIComponent(item.maMH)}/check-status`);
      if (checkRes.ok) {
          var checkData = await checkRes.json();
          if (checkData.da_dangky_thi || checkData.da_thi) {
              if (btnSua) { btnSua.disabled = true; btnSua.style.opacity = "0.4"; btnSua.style.cursor = "not-allowed"; }
              if (btnXoa) { btnXoa.disabled = true; btnXoa.style.opacity = "0.4"; btnXoa.style.cursor = "not-allowed"; }
              
              let errorMsg = "Môn học này đã được đăng ký thi. Không thể sửa/xóa!";
              showError(errorMsg);
          }
      }
  } catch (e) {
      console.error(e);
  }

  render();
};"""
js = js.replace(old_selectRow, new_selectRow)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=10', html)
with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("monHoc select behavior updated.")

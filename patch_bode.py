import re

# 1. Update formBoDe.html
with open('templates/formBoDe.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the toolbar buttons
old_buttons = """        <button id="btnSua" type="button" onclick="sua()" data-permission="update_question">Sua</button>
        <button id="btnXoa" type="button" onclick="xoa()" data-permission="delete_question">Xoa</button>
        <button id="btnUndo" type="button" onclick="undo()" data-any-permission="create_question,update_question,delete_question">Undo</button>"""

new_buttons = """        <button id="btnSua" type="button" onclick="sua()" data-permission="update_question" style="display: none;">Sua</button>
        <button id="btnXoa" type="button" onclick="xoa()" data-permission="delete_question" style="display: none;">Xoa</button>
        <button id="btnHuyChon" type="button" onclick="huy()" style="display: none;">Huy</button>
        <button id="btnUndo" type="button" onclick="undo()" data-any-permission="create_question,update_question,delete_question" style="display: none;">Undo</button>"""

if old_buttons in html:
    html = html.replace(old_buttons, new_buttons)
else:
    # Try more flexible replace
    html = re.sub(r'<button id="btnSua"[^>]*>Sua</button>', r'<button id="btnSua" type="button" onclick="sua()" data-permission="update_question" style="display: none;">Sua</button>', html)
    html = re.sub(r'<button id="btnXoa"[^>]*>Xoa</button>', r'<button id="btnXoa" type="button" onclick="xoa()" data-permission="delete_question" style="display: none;">Xoa</button>', html)
    html = re.sub(r'<button id="btnUndo"[^>]*>Undo</button>', r'<button id="btnHuyChon" type="button" onclick="huy()" style="display: none;">Huy</button>\n        <button id="btnUndo" type="button" onclick="undo()" data-any-permission="create_question,update_question,delete_question" style="display: none;">Undo</button>', html)

html = re.sub(r'boDe\.js\?v=\d+', 'boDe.js?v=10', html)

with open('templates/formBoDe.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 2. Update boDe.js
with open('static/js/boDe.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Update setButtonState
old_set_btn = """function setButtonState(state) {
  const editing = state === "editing";
  const hasSelection = selectedIndex >= 0;

  if (formPanel) formPanel.hidden = !(editing || hasSelection);
  if (formActions) formActions.hidden = !editing;
  if (btnOpenThem) btnOpenThem.style.display = editing ? "none" : "inline-flex";
  if (btnSua) btnSua.disabled = editing;
  if (btnXoa) btnXoa.disabled = editing;
  if (btnUndo) btnUndo.disabled = editing;
  if (btnGhi) btnGhi.style.display = editing ? "inline-block" : "none";
  if (btnHuy) btnHuy.style.display = editing ? "inline-block" : "none";
}"""

new_set_btn = """function setButtonState(state, daSuDung = false) {
  const editing = state === "editing";
  const hasSelection = selectedIndex >= 0;

  if (formPanel) formPanel.hidden = !(editing || hasSelection);
  if (formActions) formActions.hidden = !editing;
  
  if (state === "default") {
    if (btnOpenThem) btnOpenThem.style.display = "inline-flex";
    if (btnSua) btnSua.style.display = "none";
    if (btnXoa) btnXoa.style.display = "none";
    if (btnUndo) btnUndo.style.display = (stackUndo.length > 0) ? "inline-block" : "none";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "none";
    const btnHuyChon = document.getElementById("btnHuyChon");
    if (btnHuyChon) btnHuyChon.style.display = "none";
  } else if (state === "selected") {
    if (btnOpenThem) btnOpenThem.style.display = "none";
    if (btnSua) {
      btnSua.style.display = "inline-block";
      if (daSuDung) {
        btnSua.disabled = true;
        btnSua.style.opacity = 0.5;
        btnSua.style.cursor = "not-allowed";
        btnSua.title = "Câu hỏi đã được sử dụng trong đề thi";
      } else {
        btnSua.disabled = false;
        btnSua.style.opacity = 1;
        btnSua.style.cursor = "pointer";
        btnSua.title = "";
      }
    }
    if (btnXoa) {
      btnXoa.style.display = "inline-block";
      if (daSuDung) {
        btnXoa.disabled = true;
        btnXoa.style.opacity = 0.5;
        btnXoa.style.cursor = "not-allowed";
        btnXoa.title = "Câu hỏi đã được sử dụng trong đề thi";
      } else {
        btnXoa.disabled = false;
        btnXoa.style.opacity = 1;
        btnXoa.style.cursor = "pointer";
        btnXoa.title = "";
      }
    }
    if (btnUndo) btnUndo.style.display = "none";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "none";
    const btnHuyChon = document.getElementById("btnHuyChon");
    if (btnHuyChon) btnHuyChon.style.display = "inline-block";
  } else if (state === "editing") {
    if (btnOpenThem) btnOpenThem.style.display = "none";
    if (btnSua) btnSua.style.display = "none";
    if (btnXoa) btnXoa.style.display = "none";
    if (btnUndo) btnUndo.style.display = "none";
    if (btnGhi) btnGhi.style.display = "inline-block";
    if (btnHuy) btnHuy.style.display = "inline-block";
    const btnHuyChon = document.getElementById("btnHuyChon");
    if (btnHuyChon) btnHuyChon.style.display = "none";
  }
}"""

js = js.replace(old_set_btn, new_set_btn)

# Update selectRow
old_select = """  function selectRow(index) {
    if (isSua || isThem) {
      showError("Vui lAng Ghi hoc H y tr>c khi ch?n cAu h?i khAc!");
      return;
    }
    clearError();
  
    selectedIndex = index;
    const item = data[index];
    
    cauHoiIdInput.value = item.cauhoi;
    noiDungInput.value = item.noidung;
    dapAnAInput.value = item.a;
    dapAnBInput.value = item.b;
    dapAnCInput.value = item.c;
    dapAnDInput.value = item.d;
    dapAnDungSelect.value = item.dap_an;
    trinhDoSelect.value = item.trinhdo;
    maMHInput.value = item.mamh;
    
    // A?nh x magv sang `<nh dng "MAGV - TAn" cho A' search
    const gvInfo = window.listGiaoViens ? window.listGiaoViens.find(g => g.magv === item.magv) : null;
    if (searchGVInput) {
      searchGVInput.value = gvInfo ? `${gvInfo.magv} - ${gvInfo.hoten}` : item.magv;
    }
    maGVInput.value = item.magv;
  
    setButtonState("default");
    setFormTitle("Chi tit cAu h?i");
    disableAllInputs(true);
  
    render();
  }"""

# Since there are encoding issues with Vietnamese characters in the powershell output (e.g. A?nh x magv, Vui lAng),
# I'll use regex to match selectRow
import re

new_select = """  async function selectRow(index) {
    if (isSua || isThem) {
      showError("Vui lòng Ghi hoặc Hủy trước khi chọn câu hỏi khác!");
      return;
    }
    clearError();
  
    selectedIndex = index;
    const item = data[index];
    
    cauHoiIdInput.value = item.cauhoi;
    noiDungInput.value = item.noidung;
    dapAnAInput.value = item.a;
    dapAnBInput.value = item.b;
    dapAnCInput.value = item.c;
    dapAnDInput.value = item.d;
    dapAnDungSelect.value = item.dap_an;
    trinhDoSelect.value = item.trinhdo;
    maMHInput.value = item.mamh;
    
    const gvInfo = window.listGiaoViens ? window.listGiaoViens.find(g => g.magv === item.magv) : null;
    if (searchGVInput) {
      searchGVInput.value = gvInfo ? `${gvInfo.magv} - ${gvInfo.hoten}` : item.magv;
    }
    maGVInput.value = item.magv;
  
    let da_su_dung = false;
    if (item.cauhoi) {
      try {
        const res = await fetch(`/bode/${item.cauhoi}/check-status`);
        const statusData = await parseResponse(res);
        da_su_dung = !!statusData.da_su_dung;
      } catch (e) {
        console.error(e);
      }
    }

    setButtonState("selected", da_su_dung);
    setFormTitle("Chi tiết câu hỏi");
    disableAllInputs(true);
  
    render();
  }"""

# the selectRow function is a global function inside the script, but might be just function selectRow(index)
js = re.sub(r'function selectRow\(index\) \{[\s\S]*?render\(\);\s*\}', new_select, js)

with open('static/js/boDe.js', 'w', encoding='utf-8') as f:
    f.write(js)

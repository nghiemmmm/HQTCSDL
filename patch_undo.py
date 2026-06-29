import re

# 1. Update formBoDe.html
with open('templates/formBoDe.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove btnUndo from list actions
html = re.sub(r'<button id="btnUndo" type="button" onclick="undo\(\)".*?Undo</button>', '', html)

# Add btnUndo to formActions
if 'id="btnUndo"' not in html:
    html = re.sub(
        r'(<button id="btnGhi")',
        r'<button id="btnUndo" onclick="undo()" type="button" style="display: none; margin-right: 8px;">Undo</button>\n      \1',
        html
    )

html = re.sub(r'boDe\.js\?v=\d+', 'boDe.js?v=13', html)

with open('templates/formBoDe.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update boDe.js
with open('static/js/boDe.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Remove stackUndo
js = re.sub(r'let stackUndo\s*=\s*\[\];\s*', '', js)
js = re.sub(r'stackUndo\.push\([^;]+\);\s*', '', js)

# Update setButtonState
old_state = """    if (state === "default") {
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
      if (btnUndo) btnUndo.style.display = (stackUndo.length > 0) ? "inline-block" : "none";
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
    }"""

new_state = """    if (state === "default") {
      if (btnOpenThem) btnOpenThem.style.display = "inline-flex";
      if (btnSua) btnSua.style.display = "none";
      if (btnXoa) btnXoa.style.display = "none";
      if (btnUndo) btnUndo.style.display = "none";
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
      if (btnUndo) btnUndo.style.display = isSua ? "inline-block" : "none";
      if (btnGhi) btnGhi.style.display = "inline-block";
      if (btnHuy) btnHuy.style.display = "inline-block";
      const btnHuyChon = document.getElementById("btnHuyChon");
      if (btnHuyChon) btnHuyChon.style.display = "none";
    }"""

# Fallback regex if precise replace fails due to whitespace
js = re.sub(r'if \(state === "default"\) \{.*?if \(btnHuyChon\) btnHuyChon\.style\.display = "none";\s*\}', new_state, js, flags=re.DOTALL)

# Replace undo()
old_undo_regex = r'async function undo\(\) \{.*?\} catch \(err\) \{.*?\}.*?\}'

new_undo = """function undo() {
  clearError();
  if (!isSua || selectedIndex < 0) return;
  const item = data[selectedIndex];
  if (!item) return;
  cauHoiIdInput.value = item.cauhoi;
  noiDungInput.value = item.noidung;
  dapAnAInput.value = item.a;
  dapAnBInput.value = item.b;
  dapAnCInput.value = item.c;
  dapAnDInput.value = item.d;
  dapAnDungSelect.value = item.dap_an;
  trinhDoSelect.value = item.trinhdo;
  maMHInput.value = item.mamh;
  if (maGVInput) maGVInput.value = item.magv || "";
  if (searchGVInput) {
    const gvInfo = window.listGiaoViens ? window.listGiaoViens.find(g => g.magv === item.magv) : null;
    searchGVInput.value = gvInfo ? `${gvInfo.magv} - ${gvInfo.hoten}` : (item.magv || "");
  }
}"""

js = re.sub(old_undo_regex, new_undo, js, flags=re.DOTALL)

with open('static/js/boDe.js', 'w', encoding='utf-8') as f:
    f.write(js)

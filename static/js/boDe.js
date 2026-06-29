let data = [];
if (window.initialBodes) {
  data = window.initialBodes;
}

let selectedIndex = -1;
let isThem = false;
let isSua = false;
let editingCauHoiId = null;
const userRole = (window.currentUser?.role || window.userRole || "").trim().toUpperCase();
const userMa = (window.currentUser?.ma || window.userMa || "").trim();

// DOM Elements
const cauHoiIdInput = document.getElementById("cauHoiId");
const noiDungInput = document.getElementById("noiDung");
const dapAnAInput = document.getElementById("dapAnA");
const dapAnBInput = document.getElementById("dapAnB");
const dapAnCInput = document.getElementById("dapAnC");
const dapAnDInput = document.getElementById("dapAnD");
const dapAnDungSelect = document.getElementById("dapAnDung");
const trinhDoSelect = document.getElementById("trinhDo");
const maMHInput = document.getElementById("maMH");
const searchGVInput = document.getElementById("searchGV");
const maGVInput = document.getElementById("maGV");
const searchBoDeInput = document.getElementById("searchBoDe");
const searchTrinhDoInput = document.getElementById("searchTrinhDo");
const errorText = document.getElementById("errorText");
const formPanel = document.getElementById("questionFormPanel");
const formActions = document.getElementById("formActions");
const formTitle = document.getElementById("formTitle");
const pageSummary = document.getElementById("pageSummary");
const pageNumbers = document.getElementById("pageNumbers");
const prevPageBtn = document.getElementById("prevPageBtn");
const nextPageBtn = document.getElementById("nextPageBtn");
const pageSizeSelect = document.getElementById("pageSizeSelect");

const btnOpenThem = document.getElementById("btnOpenThem");
const btnSua = document.getElementById("btnSua");
const btnXoa = document.getElementById("btnXoa");
const btnGhi = document.getElementById("btnGhi");
const btnHuy = document.getElementById("btnHuy");
const btnUndo = document.getElementById("btnUndo");
const showTeacherColumn = userRole !== "GIANGVIEN";

let currentPage = 1;
let pageSize = parseInt(pageSizeSelect?.value || "10", 10);

function setButtonState(state, daSuDung = false) {
  const editing = state === "editing";
  const hasSelection = selectedIndex >= 0;

  if (formPanel) formPanel.hidden = !(editing || hasSelection);
  if (formActions) formActions.hidden = !editing;
  
      if (state === "default") {
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
}

function setFormTitle(text) {
  if (formTitle) formTitle.innerText = text;
}

function showError(msg) {
  if (errorText) {
    errorText.style.color = "#dc2626";
    errorText.innerText = msg;
  }
}
function showSuccess(msg) {
  if (errorText) {
    errorText.style.color = "#16a34a";
    errorText.innerText = msg;
  }
}
function clearError() {
  if (errorText) {
    errorText.innerText = "";
    errorText.style.color = "#dc2626";
  }
}

function normalizeAnswerText(value) {
  return (value || "").trim().toLowerCase();
}

function checkDuplicateAnswers(question) {
    const a = normalizeAnswerText(question.a);
    const b = normalizeAnswerText(question.b);
    const c = normalizeAnswerText(question.c);
    const d = normalizeAnswerText(question.d);

    if (a === b) return "Đáp án A trùng đáp án B";
    if (a === c) return "Đáp án A trùng đáp án C";
    if (a === d) return "Đáp án A trùng đáp án D";
    if (b === c) return "Đáp án B trùng đáp án C";
    if (b === d) return "Đáp án B trùng đáp án D";
    if (c === d) return "Đáp án C trùng đáp án D";

    return null;
  }

async function parseResponse(res) {
  let resData = {};
  try {
    resData = await res.json();
  } catch {
    resData = {};
  }
  if (!res.ok) {
    let msg = "Lỗi không xác định";
    if (resData.detail) {
      if (typeof resData.detail === "string") {
        msg = resData.detail;
      } else if (typeof resData.detail === "object") {
        if (resData.detail.message) {
          msg = resData.detail.message;
        } else if (Array.isArray(resData.detail)) {
          msg = resData.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join("; ");
        } else {
          msg = JSON.stringify(resData.detail);
        }
      }
    } else if (resData.message) {
      msg = resData.message;
    }
    throw new Error(msg);
  }
  return resData;
}

function getFilteredRows() {
  const selectedMaMH = searchBoDeInput ? searchBoDeInput.value.trim() : "";
  const selectedTrinhDo = searchTrinhDoInput ? searchTrinhDoInput.value.trim() : "";
  
  return data
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => {
      if (selectedMaMH && (item.mamh || "").trim() !== selectedMaMH) return false;
      if (selectedTrinhDo && (item.trinhdo || "").trim() !== selectedTrinhDo) return false;
      return true;
    });
}

function clampCurrentPage(totalPages) {
  currentPage = Math.min(Math.max(currentPage, 1), Math.max(totalPages, 1));
}

function renderPagination(totalRows, totalPages) {
  if (pageSummary) {
    if (!totalRows) {
      pageSummary.innerText = "Khong co cau hoi phu hop";
    } else {
      const from = (currentPage - 1) * pageSize + 1;
      const to = Math.min(currentPage * pageSize, totalRows);
      pageSummary.innerText = `Hien thi ${from}-${to} trong ${totalRows} cau hoi`;
    }
  }

  if (prevPageBtn) prevPageBtn.disabled = currentPage <= 1;
  if (nextPageBtn) nextPageBtn.disabled = currentPage >= totalPages;

  if (!pageNumbers) return;
  pageNumbers.innerHTML = "";

  const maxButtons = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
  let endPage = Math.min(totalPages, startPage + maxButtons - 1);
  startPage = Math.max(1, endPage - maxButtons + 1);

  for (let page = startPage; page <= endPage; page++) {
    const button = document.createElement("button");
    button.type = "button";
    button.innerText = page;
    if (page === currentPage) button.classList.add("is-active");
    button.addEventListener("click", () => {
      currentPage = page;
      render();
    });
    pageNumbers.appendChild(button);
  }
}

function render() {
  const tbody = document.getElementById("tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const filteredRows = getFilteredRows();
  const totalRows = filteredRows.length;
  const totalPages = Math.ceil(totalRows / pageSize) || 1;
  clampCurrentPage(totalPages);

  const startIndex = (currentPage - 1) * pageSize;
  const pageRows = filteredRows.slice(startIndex, startIndex + pageSize);

  if (!pageRows.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="${showTeacherColumn ? 6 : 5}" class="empty-cell">Khong co cau hoi phu hop.</td>`;
    tbody.appendChild(row);
  }

  pageRows.forEach(({ item, index }) => {
    const row = document.createElement("tr");

    if (index === selectedIndex) {
      row.classList.add("is-selected");
    }

    const gvInfo = window.listGiaoViens ? window.listGiaoViens.find(g => g.magv === item.magv) : null;
    const gvDisplay = gvInfo ? `${gvInfo.magv} - ${gvInfo.hoten}` : item.magv;

    row.innerHTML = `
      <td>${item.cauhoi}</td>
      <td>${item.noidung && item.noidung.length > 70 ? item.noidung.substring(0, 70) + '...' : item.noidung}</td>
      <td>${item.mamh}</td>
      <td>${item.trinhdo}</td>
      <td>${item.dap_an}</td>
      ${showTeacherColumn ? `<td>${gvDisplay}</td>` : ""}
    `;

    row.onclick = () => selectRow(index);
    tbody.appendChild(row);
  });

  renderPagination(totalRows, totalPages);
}

  async function selectRow(index) {
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
  }

function disableAllInputs(disabled) {
  noiDungInput.disabled = disabled;
  dapAnAInput.disabled = disabled;
  dapAnBInput.disabled = disabled;
  dapAnCInput.disabled = disabled;
  dapAnDInput.disabled = disabled;
  dapAnDungSelect.disabled = disabled;
  trinhDoSelect.disabled = disabled;
  maMHInput.disabled = disabled;
  if (searchGVInput) searchGVInput.disabled = disabled;
}

function clearForm() {
  cauHoiIdInput.value = "";
  noiDungInput.value = "";
  dapAnAInput.value = "";
  dapAnBInput.value = "";
  dapAnCInput.value = "";
  dapAnDInput.value = "";
  dapAnDungSelect.value = "";
  trinhDoSelect.value = "";
  maMHInput.value = "";
  if (searchGVInput) searchGVInput.value = "";
  maGVInput.value = "";
}

function them() {
  clearError();
  isThem = true;
  isSua = false;
  selectedIndex = -1;
  editingCauHoiId = null;
  setFormTitle("Them cau hoi");
  setButtonState("editing");
  
  clearForm();
  disableAllInputs(false);
  noiDungInput.focus();

  render();
}

async function sua() {
  clearError();
  if (selectedIndex < 0) return showError("Vui lòng chọn dòng cần sửa");

  const cauhoiId = data[selectedIndex].cauhoi;
  try {
    const res = await fetch(`/bode/${cauhoiId}/check-status`);
    const statusData = await parseResponse(res);
    if (statusData.da_su_dung) {
      return showError("Câu hỏi này đã được sử dụng trong đề thi, không thể sửa!");
    }
  } catch (err) {
    return showError(err.message);
  }

  isSua = true;
  isThem = false;
  editingCauHoiId = cauhoiId;
  setFormTitle("Sua cau hoi");
  setButtonState("editing");

  disableAllInputs(false);
  noiDungInput.focus();
}

async function ghi() {
  clearError();

  // Xác định magv dựa trên role
  let magv = "";
  if (userRole === "GIANGVIEN") {
    magv = userMa;
  } else {
    magv = searchGVInput ? searchGVInput.value.split(" - ")[0].trim() : "";
  }

  const obj = {
    noidung: noiDungInput.value.trim(),
    a: dapAnAInput.value.trim(),
    b: dapAnBInput.value.trim(),
    c: dapAnCInput.value.trim(),
    d: dapAnDInput.value.trim(),
    dap_an: dapAnDungSelect.value,
    trinhdo: trinhDoSelect.value,
    mamh: maMHInput.value.trim(),
    magv: magv
  };

  if (!obj.noidung) return showError("Nội dung câu hỏi không được để trống!");
  if (!obj.a) return showError("Đáp án A không được để trống!");
  if (!obj.b) return showError("Đáp án B không được để trống!");
  if (!obj.c) return showError("Đáp án C không được để trống!");
  if (!obj.d) return showError("Đáp án D không được để trống!");
  if (!obj.dap_an) return showError("Vui lòng chọn đáp án đúng!");
  if (!obj.trinhdo) return showError("Vui lòng chọn trình độ!");
  if (!obj.mamh) return showError("Mã môn học không được để trống!");
  const duplicateError = checkDuplicateAnswers(obj);
    if (duplicateError) return showError(duplicateError);
  // Chỉ kiểm tra magv nếu không phải giáo viên
  if (userRole !== "GIANGVIEN" && !obj.magv) return showError("Mã giáo viên không được để trống!");

  try {
    let res, resData;

    if (isThem) {
      res = await fetch("/bode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj)
      });

      resData = await parseResponse(res);
      const result = resData.data;
      data.push(result);
      currentPage = Math.ceil(getFilteredRows().length / pageSize) || 1;

      isThem = false;
      showSuccess(resData.message);
    } 
    else if (isSua) {
      const old = { ...data[selectedIndex] };

      res = await fetch(`/bode/${editingCauHoiId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj)
      });

      resData = await parseResponse(res);
      const result = resData.data;
      data[selectedIndex] = result;

      isSua = false;
      showSuccess(resData.message);
    }

  } catch (err) {
    return showError(err.message);
  }

  disableAllInputs(true);
  clearForm();
  selectedIndex = -1;
  setButtonState("default");

  render();
}

function huy() {
  clearError();
  isSua = false;
  isThem = false;
  editingCauHoiId = null;

  clearForm();
  disableAllInputs(true);
  
  selectedIndex = -1;
  setButtonState("default");
  render();
}

async function xoa() {
  clearError();
  if (selectedIndex < 0) return showError("Vui lòng chọn dòng cần xóa");

  const rowData = data[selectedIndex];

  try {
    const res = await fetch(`/bode/${rowData.cauhoi}/check-status`);
    const statusData = await parseResponse(res);
    if (statusData.da_su_dung) {
      return showError("Câu hỏi này đã được sử dụng trong đề thi, không thể xoá!");
    }
  } catch (err) {
    return showError(err.message);
  }
  
  errorText.innerHTML = `
    <div style="background: #fee2e2; border: 1px solid #f87171; padding: 10px; border-radius: 4px; display: inline-block; color: #991b1b;">
      Ban co muon xoa cau hoi ID <b>${rowData.cauhoi}</b>?
      <div style="margin-top: 8px;">
        <button onclick="thucHienXoa()" style="background: #ef4444; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px;">Xoa</button>
        <button onclick="huyXoa()" style="background: #e5e7eb; color: #374151; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer;">Huy</button>
      </div>
    </div>
  `;
}

function huyXoa() {
  clearError();
}

async function thucHienXoa() {
  const itemToDel = data[selectedIndex];
  try {
    const res = await fetch(`/bode/${itemToDel.cauhoi}`, { method: "DELETE" });
    const resData = await parseResponse(res);

    data.splice(selectedIndex, 1);

    selectedIndex = -1;
    clearForm();
    disableAllInputs(true);
    clearError();
    showSuccess(resData.message);

    render();

  } catch (err) {
    showError(err.message);
  }
}

function undo() {
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
}

document.addEventListener("DOMContentLoaded", () => {
  setButtonState("default");
  render();

  const onFilterChange = () => {
    selectedIndex = -1;
    currentPage = 1;
    clearForm();
    disableAllInputs(true);
    render();
  };
  
  if (searchBoDeInput) {
    searchBoDeInput.addEventListener("change", onFilterChange);
  }
  if (searchTrinhDoInput) {
    searchTrinhDoInput.addEventListener("change", onFilterChange);
  }

  prevPageBtn?.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      render();
    }
  });

  nextPageBtn?.addEventListener("click", () => {
    currentPage++;
    render();
  });

  pageSizeSelect?.addEventListener("change", () => {
    pageSize = parseInt(pageSizeSelect.value, 10) || 10;
    currentPage = 1;
    render();
  });
});

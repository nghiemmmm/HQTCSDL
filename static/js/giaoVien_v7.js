let data = [];
if (window.initialGiaoViens) {
  data = window.initialGiaoViens.map(item => ({
    magv: item.magv,
    ho: item.ho || "",
    ten: item.ten || "",
    diachi: item.diachi || "",
    sodtll: item.sodtll || ""
  }));
}

let selectedIndex = -1;
let isThem = false;
let isSua = false;
let editingMa = null;
let stackUndo = [];
let pageSize = 10;
let currentPage = 1;

const maGVInput = document.getElementById("maGV");
const hoGVInput = document.getElementById("hoGV");
const tenGVInput = document.getElementById("tenGV");
const diaChiGVInput = document.getElementById("diaChiGV");
const sdtGVInput = document.getElementById("sdtGV");

const searchGVInput = document.getElementById("searchGV");
const errorText = document.getElementById("errorText");

const btnThem = document.getElementById("btnThem");
const btnSua = document.getElementById("btnSua");
const btnXoa = document.getElementById("btnXoa");
const btnGhi = document.getElementById("btnGhi");
const btnHuy = document.getElementById("btnHuy");
const btnUndo = document.getElementById("btnUndo");

function setButtonState(state) {
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

async function parseResponse(res) {
  let resData = {};
  try {
    resData = await res.json();
  } catch {
    resData = {};
  }
  if (!res.ok) {
    const detail = resData.detail;
    const message = detail?.message || detail?.detail || resData.message || detail;
    throw new Error(typeof message === "string" ? message : "Loi khong xac dinh");
  }
  return resData;
}

function getFilteredRows() {
  const keyword = searchGVInput ? searchGVInput.value.trim().toLowerCase() : "";
  return data
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => {
      if (!keyword) return true;
      const matchMagv = (item.magv || "").toLowerCase().includes(keyword);
      const matchHo = (item.ho || "").toLowerCase().includes(keyword);
      const matchTen = (item.ten || "").toLowerCase().includes(keyword);
      return matchMagv || matchHo || matchTen;
    });
}

function renderPagination(totalRows, totalPages) {
  const container = document.getElementById("giaoVienPagination");
  if (!container) return;
  if (totalRows <= pageSize) {
    container.innerHTML = totalRows ? `Hien thi ${totalRows}/${totalRows}` : "Khong co du lieu";
    return;
  }
  const from = (currentPage - 1) * pageSize + 1;
  const to = Math.min(currentPage * pageSize, totalRows);
  let buttons = "";
  for (let page = 1; page <= totalPages; page++) {
    buttons += `<button type="button" class="${page === currentPage ? "is-active" : ""}" onclick="goToGiaoVienPage(${page})">${page}</button>`;
  }
  container.innerHTML = `
    <span>Hien thi ${from}-${to} trong ${totalRows}</span>
    <button type="button" ${currentPage <= 1 ? "disabled" : ""} onclick="goToGiaoVienPage(${currentPage - 1})">Truoc</button>
    ${buttons}
    <button type="button" ${currentPage >= totalPages ? "disabled" : ""} onclick="goToGiaoVienPage(${currentPage + 1})">Sau</button>
  `;
}

window.goToGiaoVienPage = function(page) {
  currentPage = page;
  render();
};

function render() {
  const tbody = document.getElementById("tbody");
  tbody.innerHTML = "";

  const rows = getFilteredRows();
  const totalRows = rows.length;
  const totalPages = Math.ceil(totalRows / pageSize) || 1;
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  const start = (currentPage - 1) * pageSize;
  const pageRows = rows.slice(start, start + pageSize);

  if (!pageRows.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="5">Khong co du lieu</td>`;
    tbody.appendChild(row);
  }

  pageRows.forEach(({ item, index }) => {
    const row = document.createElement("tr");

    if (index === selectedIndex) {
      row.style.background = "#d1e7ff";
    }

    row.innerHTML = `
      <td>${item.magv}</td>
      <td>${item.ho}</td>
      <td>${item.ten}</td>
      <td>${item.diachi}</td>
      <td>${item.sodtll}</td>
    `;

    row.onclick = () => selectRow(index);
    tbody.appendChild(row);
  });

  renderPagination(totalRows, totalPages);
}

function selectRow(index) {
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

  render();
}

function them() {
  clearError();
  isThem = true;
  isSua = false;
  selectedIndex = -1;
  setButtonState("editing");

  maGVInput.disabled = false;
  hoGVInput.disabled = false;
  tenGVInput.disabled = false;
  diaChiGVInput.disabled = false;
  sdtGVInput.disabled = false;
  
  maGVInput.style.backgroundColor = "";
  
  maGVInput.value = "";
  hoGVInput.value = "";
  tenGVInput.value = "";
  diaChiGVInput.value = "";
  sdtGVInput.value = "";
  
  maGVInput.focus();

  render();
}

function sua() {
  clearError();
  if (selectedIndex < 0) return showError("Vui lòng chọn dòng cần sửa");

  isSua = true;
  isThem = false;
  editingMa = data[selectedIndex].magv;
  setButtonState("editing");

  maGVInput.disabled = true;
  maGVInput.style.backgroundColor = "#e5e7eb";
  
  hoGVInput.disabled = false;
  tenGVInput.disabled = false;
  diaChiGVInput.disabled = false;
  sdtGVInput.disabled = false;

  hoGVInput.focus();
}

async function ghi() {
  clearError();

  const obj = {
    magv: maGVInput.value.trim(),
    ho: hoGVInput.value.trim(),
    ten: tenGVInput.value.trim(),
    diachi: diaChiGVInput.value.trim(),
    sodtll: sdtGVInput.value.trim()
  };

  if (!obj.magv) return showError("Mã giáo viên không được để trống!");
  if (obj.magv.length > 8) return showError("Mã giáo viên tối đa 8 ký tự!");
  if (!obj.ho) return showError("Họ giáo viên không được để trống!");
  if (!obj.ten) return showError("Tên giáo viên không được để trống!");
  if (obj.ho.length > 40) return showError("Họ giáo viên tối đa 40 ký tự!");
  if (obj.ten.length > 10) return showError("Tên giáo viên tối đa 10 ký tự!");
  if (obj.diachi.length > 50) return showError("Địa chỉ tối đa 50 ký tự!");
  if (obj.sodtll.length > 15) return showError("Số điện thoại tối đa 15 ký tự!");

  try {
    let res, resData;

    if (isThem) {
      res = await fetch("/giaovien", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj)
      });

      resData = await parseResponse(res);
      const result = resData.data;
      data.push(result);
      currentPage = Math.ceil(getFilteredRows().length / pageSize) || 1;
      stackUndo.push({ type: "ADD", data: result });

      isThem = false;
      showSuccess(resData.message);
    } 
    else if (isSua) {
      const old = { ...data[selectedIndex] };

      res = await fetch(`/giaovien/${editingMa}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj)
      });

      resData = await parseResponse(res);
      const result = resData.data;
      data[selectedIndex] = result;

      stackUndo.push({ type: "UPDATE", old, new: result, index: selectedIndex });

      isSua = false;
      showSuccess(resData.message);
    }

  } catch (err) {
    return showError(err.message);
  }

  maGVInput.disabled = true;
  hoGVInput.disabled = true;
  tenGVInput.disabled = true;
  diaChiGVInput.disabled = true;
  sdtGVInput.disabled = true;
  
  maGVInput.style.backgroundColor = "";
  
  maGVInput.value = "";
  hoGVInput.value = "";
  tenGVInput.value = "";
  diaChiGVInput.value = "";
  sdtGVInput.value = "";
  
  selectedIndex = -1;
  setButtonState("default");

  render();
}

function huy() {
  clearError();
  isSua = false;
  isThem = false;
  editingMa = null;

  maGVInput.value = "";
  hoGVInput.value = "";
  tenGVInput.value = "";
  diaChiGVInput.value = "";
  sdtGVInput.value = "";
  
  maGVInput.disabled = true;
  hoGVInput.disabled = true;
  tenGVInput.disabled = true;
  diaChiGVInput.disabled = true;
  sdtGVInput.disabled = true;
  
  maGVInput.style.backgroundColor = "";

  selectedIndex = -1;
  setButtonState("default");
  render();
}

function xoa() {
  clearError();
  if (selectedIndex < 0) return showError("Vui lòng chọn dòng cần xóa");

  const rowData = data[selectedIndex];
  
  // Kiểm tra xem giáo viên có thể xóa hay không
  (async () => {
    try {
      console.log(`Checking status for teacher: /giaovien/${rowData.magv}/check-status`);
      const checkRes = await fetch(`/giaovien/${rowData.magv}/check-status`);
      console.log("Check response status:", checkRes.status);
      
      const checkData = await checkRes.json();
      console.log("Check data:", checkData);

      if (checkData.co_gan_mon || checkData.co_cauhoi) {
        // Nếu giáo viên được gán môn hoặc có câu hỏi, không cho xóa
        let errorMsg = "Giáo viên này ";
        if (checkData.co_gan_mon && checkData.co_cauhoi) {
          errorMsg += "đã được gán dạy và có soạn câu hỏi";
        } else if (checkData.co_gan_mon) {
          errorMsg += "đã được gán dạy môn";
        } else {
          errorMsg += "có soạn câu hỏi";
        }
        errorMsg += ". Không thể xóa!";
        console.log(errorMsg);
        showError(errorMsg);
        return;
      }

      // Nếu không, hiển thị dialog xác nhận
      errorText.innerHTML = `
        <div style="background: #fee2e2; border: 1px solid #f87171; padding: 10px; border-radius: 4px; display: inline-block; color: #991b1b;">
          Ban co muon xoa giao vien <b>${rowData.ho} ${rowData.ten}</b>?
          <div style="margin-top: 8px;">
            <button onclick="thucHienXoa()" style="background: #ef4444; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px;">Xoa</button>
            <button onclick="huyXoa()" style="background: #e5e7eb; color: #374151; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer;">Huy</button>
          </div>
        </div>
      `;
    } catch (err) {
      console.error("Error in xoa:", err);
      showError(err.message);
    }
  })();
}

function huyXoa() {
  clearError();
}

async function thucHienXoa() {
  const itemToDel = data[selectedIndex];
  try {
    const res = await fetch(`/giaovien/${itemToDel.magv}`, { method: "DELETE" });
    const resData = await parseResponse(res);

    stackUndo.push({ type: "DELETE", data: itemToDel });
    data.splice(selectedIndex, 1);

    selectedIndex = -1;
    clearError();
    showSuccess(resData.message);

    render();

  } catch (err) {
    showError(err.message);
  }
}

async function undo() {
  clearError();
  if (stackUndo.length === 0) return showError("Không có thao tác nào để Undo!");
  if (isThem || isSua) return showError("Vui lòng Ghi hoặc Hủy thao tác hiện tại trước khi Undo!");

  const action = stackUndo.pop();

  try {
    if (action.type === "ADD") {
      const res = await fetch(`/giaovien/${action.data.magv}`, { method: "DELETE" });
      const resData = await parseResponse(res);
      showSuccess("Undo: " + resData.message);
      data.pop();
    }

    if (action.type === "DELETE") {
      const res = await fetch("/giaovien", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(action.data)
      });
      const resData = await parseResponse(res);
      showSuccess("Undo: " + resData.message);
      data.push(action.data);
    }

    if (action.type === "UPDATE") {
      const res = await fetch(`/giaovien/${action.new.magv}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(action.old)
      });
      const resData = await parseResponse(res);
      showSuccess("Undo: " + resData.message);
      data[action.index] = action.old;
    }

    selectedIndex = -1;
    render();
  } catch (err) {
    showError("Undo thất bại: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setButtonState("default");
  render();

  if (searchGVInput) {
    searchGVInput.addEventListener("input", () => {
      selectedIndex = -1;
      currentPage = 1;
      render();
    });
  }
});

function checkDuplicateGV() {
  if (isThem) {
    const val = maGVInput.value.trim();
    if (val) {
      const exists = data.some(item => (item.magv || "").trim().toLowerCase() === val.toLowerCase());
      if (exists) {
        showError(`Mã giáo viên ${val} đã tồn tại`);
        if (btnGhi) btnGhi.disabled = true;
        hoGVInput.disabled = true;
        tenGVInput.disabled = true;
        diaChiGVInput.disabled = true;
        sdtGVInput.disabled = true;
        hoGVInput.style.backgroundColor = "#e5e7eb";
        tenGVInput.style.backgroundColor = "#e5e7eb";
        diaChiGVInput.style.backgroundColor = "#e5e7eb";
        sdtGVInput.style.backgroundColor = "#e5e7eb";
      } else {
        clearError();
        if (btnGhi) btnGhi.disabled = false;
        hoGVInput.disabled = false;
        tenGVInput.disabled = false;
        diaChiGVInput.disabled = false;
        sdtGVInput.disabled = false;
        hoGVInput.style.backgroundColor = "";
        tenGVInput.style.backgroundColor = "";
        diaChiGVInput.style.backgroundColor = "";
        sdtGVInput.style.backgroundColor = "";
      }
    } else {
      clearError();
      if (btnGhi) btnGhi.disabled = false;
      hoGVInput.disabled = false;
      tenGVInput.disabled = false;
      diaChiGVInput.disabled = false;
      sdtGVInput.disabled = false;
      hoGVInput.style.backgroundColor = "";
      tenGVInput.style.backgroundColor = "";
      diaChiGVInput.style.backgroundColor = "";
      sdtGVInput.style.backgroundColor = "";
    }
  }
}

if (maGVInput) {
  ['input', 'change', 'keyup'].forEach(evt => {
    maGVInput.addEventListener(evt, checkDuplicateGV);
  });
}

function blockSpecialChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[a-zA-Z0-9]+$/.test(e.key)) {
        e.preventDefault();
    }
}
function sanitizeInput(e) {
    e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
}
if (maGVInput) {
    maGVInput.addEventListener('keydown', blockSpecialChars);
    maGVInput.addEventListener('input', sanitizeInput);
}


if (hoGVInput) {
    
    
}
if (tenGVInput) {
    
    
}

function forceUppercase(e) {
    const start = e.target.selectionStart;
    const end = e.target.selectionEnd;
    e.target.value = e.target.value.toUpperCase();
    e.target.setSelectionRange(start, end);
}

function formatNameOnBlur(e) {
    let val = e.target.value;
    if (!val) return;
    val = val.replace(/[^\p{L}\s]/gu, '');
    val = val.replace(/\s+/g, ' ').trim();
    val = val.toLowerCase().replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
    e.target.value = val;
}

if (maGVInput) {
    maGVInput.addEventListener('input', forceUppercase);
}
if (hoGVInput) {
    hoGVInput.addEventListener('blur', formatNameOnBlur);
}
if (tenGVInput) {
    tenGVInput.addEventListener('blur', formatNameOnBlur);
}

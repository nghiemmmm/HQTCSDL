console.log("JS NEW VERSION LOADED");

// Chuyển toàn bộ let/const thành var để tránh lỗi khai báo lại khi load nhiều lần
var data = [];
var selectedIndex = -1;
var isSua = false;
var isThem = false;
var editingMa = null;
var stackUndo = [];
var pageSize = 10;
var currentPage = 1;

var maMHInput = document.getElementById("maMH");
var tenMHInput = document.getElementById("tenMH");
var searchTenMHInput = document.getElementById("searchTenMH");
var stateText = document.getElementById("stateText");
var errorText = document.getElementById("errorText");
var formGrid = document.getElementById("formGrid");

var btnThem = document.getElementById("btnThem");
var btnSua = document.getElementById("btnSua");
var btnXoa = document.getElementById("btnXoa");
var btnGhi = document.getElementById("btnGhi");
var btnHuy = document.getElementById("btnHuy");
var btnUndo = document.getElementById("btnUndo");

function setButtonState(state) {
  var showUndo = stackUndo.length > 0 ? "inline-block" : "none";
  
  // Reset opacity/disabled
  if (btnSua) { btnSua.disabled = false; btnSua.style.opacity = "1"; btnSua.style.cursor = "pointer"; }
  if (btnXoa) { btnXoa.disabled = false; btnXoa.style.opacity = "1"; btnXoa.style.cursor = "pointer"; }
  
  if (state === "initial") {
    if (btnThem) btnThem.style.display = "inline-block";
    if (btnSua) btnSua.style.display = "none";
    if (btnXoa) btnXoa.style.display = "none";
    if (btnUndo) btnUndo.style.display = "none";
    if (btnGhi) btnGhi.style.display = "none";
    if (btnHuy) btnHuy.style.display = "none";
  } else if (state === "default") {
    if (btnThem) btnThem.style.display = "inline-block";
    if (btnSua) btnSua.style.display = "inline-block";
    if (btnXoa) btnXoa.style.display = "inline-block";
    if (btnUndo) btnUndo.style.display = "none";
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
}

// ======================
// HELPER
// ======================
function showError(msg) {
  if (errorText) {
    errorText.style.color = "#dc2626";
    errorText.innerText = msg;
    if (window.messageTimeout) clearTimeout(window.messageTimeout);
    window.messageTimeout = setTimeout(() => {
      if (errorText.innerText === msg) errorText.innerText = "";
    }, 5000);
  }
}
function showSuccess(msg) {
  if (errorText) {
    errorText.style.color = "#16a34a";
    errorText.innerText = msg;
    if (window.messageTimeout) clearTimeout(window.messageTimeout);
    window.messageTimeout = setTimeout(() => {
      if (errorText.innerText === msg) errorText.innerText = "";
    }, 5000);
  }
}
function clearError() {
  if (errorText) {
    errorText.innerText = "";
    errorText.style.color = "#dc2626";
  }
}
function setState(msg) {
  if (stateText) stateText.innerText = msg;
}

// ✅ PARSE RESPONSE CHUẨN
async function parseResponse(res) {
  var resData = {};
  try {
    resData = await res.json();
  } catch {
    resData = {};
  }

  if (!res.ok) {
    var detail = resData.detail;
    var message = detail?.message || detail?.detail || resData.message || detail;
    throw new Error(typeof message === "string" ? message : "Lỗi không xác định");
  }

  return resData;
}

// ======================
// INIT
// ======================
// Đổi từ DOMContentLoaded sang setTimeout để chạy ngay lập tức khi inject script
setTimeout(async () => {
  try {
    console.log("Đang gọi API /monhoc/danhsachMH ...");
    var res = await fetch("/monhoc/danhsachMH");
    console.log("Status API:", res.status);
    
    var jsonList = await parseResponse(res);
    console.log("Dữ liệu nhận được:", jsonList);

    data = (jsonList || []).map(item => ({
      maMH: item.mamh,
      tenMH: item.tenmh
    }));
  } catch (err) {
    console.error("CHI TIẾT LỖI FETCH:", err);
    data = [];
    showError("Không thể tải danh sách môn học: " + err.message);
  }

  if(maMHInput) maMHInput.disabled = true;
  if(tenMHInput) tenMHInput.disabled = true;

  render();
  setState(`Đã load ${data.length} môn học`);
  setButtonState("initial");

  if (searchTenMHInput) {
    searchTenMHInput.addEventListener("input", () => {
      if (isSua) return;

      clearError();
      selectedIndex = -1;
      currentPage = 1;
      render();

      var keyword = searchTenMHInput.value.trim().toLowerCase();
      if (!keyword) {
        setState(`Đã load ${data.length} môn học`);
        return;
      }

      var count = data.filter(item => (item.tenMH || "").toLowerCase().includes(keyword)).length;
      setState(`Tìm thấy ${count} môn học khớp với "${keyword}"`);
    });
  }
}, 0);

// ======================
// RENDER
// ======================
function getFilteredRows() {
  var keyword = searchTenMHInput ? searchTenMHInput.value.trim().toLowerCase() : "";
  return data
    .map((item, index) => ({ item: item, index: index }))
    .filter(({ item }) => !keyword || (item.tenMH || "").toLowerCase().includes(keyword));
}

function renderPagination(totalRows, totalPages) {
  var container = document.getElementById("monHocPagination");
  if (!container) return;
  if (totalRows <= pageSize) {
    container.innerHTML = totalRows ? `Hien thi ${totalRows}/${totalRows}` : "Khong co du lieu";
    return;
  }
  var from = (currentPage - 1) * pageSize + 1;
  var to = Math.min(currentPage * pageSize, totalRows);
  var buttons = "";
  for (var page = 1; page <= totalPages; page++) {
    buttons += `<button type="button" class="${page === currentPage ? "is-active" : ""}" onclick="goToMonHocPage(${page})">${page}</button>`;
  }
  container.innerHTML = `
    <span>Hien thi ${from}-${to} trong ${totalRows}</span>
    <button type="button" ${currentPage <= 1 ? "disabled" : ""} onclick="goToMonHocPage(${currentPage - 1})">Truoc</button>
    ${buttons}
    <button type="button" ${currentPage >= totalPages ? "disabled" : ""} onclick="goToMonHocPage(${currentPage + 1})">Sau</button>
  `;
}

window.goToMonHocPage = function(page) {
  currentPage = page;
  render();
};

function render() {
  var tbody = document.getElementById("tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  var rows = getFilteredRows();
  var totalRows = rows.length;
  var totalPages = Math.ceil(totalRows / pageSize) || 1;
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  var start = (currentPage - 1) * pageSize;
  var pageRows = rows.slice(start, start + pageSize);

  if (!pageRows.length) {
    var emptyRow = document.createElement("tr");
    emptyRow.innerHTML = `<td colspan="2">Khong co du lieu</td>`;
    tbody.appendChild(emptyRow);
  }

  pageRows.forEach(({ item, index }) => {
    var row = document.createElement("tr");

    if (index === selectedIndex) {
      row.style.background = "#d1e7ff";
    }

    row.innerHTML = `
      <td>${item.maMH}</td>
      <td>${item.tenMH}</td>
    `;

    row.onclick = () => selectRow(index);
    tbody.appendChild(row);
  });

  renderPagination(totalRows, totalPages);
}

// ======================
// SELECT
// ======================
window.selectRow = async function(index) {
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
              if (btnSua) { btnSua.disabled = false; btnSua.style.opacity = "0.4"; btnSua.style.cursor = "pointer"; }
              if (btnXoa) { btnXoa.disabled = false; btnXoa.style.opacity = "0.4"; btnXoa.style.cursor = "pointer"; }
          }
      }
  } catch (e) {
      console.error(e);
  }

  render();
};

// ======================
// VALIDATE
// ======================


function validate() {
  var ma = maMHInput ? maMHInput.value.trim() : "";
  var ten = tenMHInput ? tenMHInput.value.trim() : "";

  if (isThem && !ma) {
    showError("Vui lòng nhập Mã môn học.");
    return false;
  }
  
  if (isThem && ma) {
    var val = ma.toUpperCase();
    var exists = data.some(function(item) { 
      return item.maMH && item.maMH.trim().toUpperCase() === val; 
    });
    if (exists) {
        showError("Mã môn học đã tồn tại trong danh sách!");
        return false;
    }
  }

  if (!ten) {
    showError("Vui lòng nhập đầy đủ Tên môn học.");
    return false;
  }
  if (ten.length > 50) {
    showError("Tên môn học không được vượt quá 50 ký tự.");
    return false;
  }
  return true;
}

// ======================
// ACTIONS
// ======================
window.them = function() {
  clearError();
  isThem = true;
  isSua = false;
  selectedIndex = -1;
  setButtonState("editing");
  if (formGrid) formGrid.style.display = "grid";

  if(maMHInput) {
        maMHInput.disabled = false;
        maMHInput.style.backgroundColor = "";
        maMHInput.value = "";
        setTimeout(() => { maMHInput.focus(); }, 50);
    }
  if(tenMHInput) {
      tenMHInput.disabled = false;
      tenMHInput.value = "";
      
  }

  render();
};

window.sua = async function() {
  clearError();
  if (selectedIndex < 0) return showError("Vui lòng chọn dòng cần sửa");

  var item = data[selectedIndex];

  try {
    // Kiểm tra xem môn học đó có được đăng ký hay không
    console.log(`Checking status for edit: /monhoc/${item.maMH}/check-status`);
    var checkRes = await fetch(`/monhoc/${item.maMH}/check-status`);
    console.log("Check response status:", checkRes.status);
    
    var checkData = await parseResponse(checkRes);
    console.log("Check data:", checkData);

    if (checkData.da_dangky_thi) {
      // Nếu đã được đăng ký, hiển thị thông báo
      console.log("Môn học đã được đăng ký, không cho sửa");
      showError("Môn này đã được đăng ký. Không thể sửa!");
      return;
    }

    // Nếu chưa được đăng ký, cho phép sửa
    console.log("Môn học chưa được đăng ký, cho phép sửa");
    isSua = true;
    isThem = false;
    editingMa = data[selectedIndex].maMH;
    setButtonState("editing");

    if(maMHInput) {
        maMHInput.disabled = true;
        maMHInput.style.backgroundColor = "#e5e7eb";
    }
    if(tenMHInput) {
        tenMHInput.disabled = false;
        
    }
  } catch (err) {
    console.error("Error in sua:", err);
    showError(err.message);
  }
};

// ======================
// GHI (ADD / UPDATE)
// ======================
window.ghi = async function() {
  clearError();
  if (!isSua && !isThem) return showError("Vui lòng bấm Thêm hoặc Sửa trước khi Ghi!");
  if (!validate()) return;

  var obj = {
    mamh: maMHInput.value.trim(),
    tenmh: tenMHInput.value.trim()
  };

  try {
    var res, resData;

    // ADD
    if (isThem) {
      res = await fetch("/monhoc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj)
      });

      resData = await parseResponse(res);

      var result = resData.data;
      data.push({ maMH: result.mamh, tenMH: result.tenmh });
      currentPage = Math.ceil(getFilteredRows().length / pageSize) || 1;
      stackUndo.push({ type: "ADD", data: result });

      isThem = false;
      showSuccess(resData.message);
    }

    // UPDATE
    else if (isSua) {
      var old = { ...data[selectedIndex] };

      res = await fetch(`/monhoc/${editingMa}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(obj)
      });

      resData = await parseResponse(res);

      var result2 = resData.data;
      data[selectedIndex] = { maMH: result2.mamh, tenMH: result2.tenmh };

      stackUndo.push({ type: "UPDATE", old: old, new: data[selectedIndex], index: selectedIndex });

      isSua = false;
      showSuccess(resData.message);
    }

  } catch (err) {
    return showError(err.message);
  }

  if(maMHInput) {
      maMHInput.disabled = true;
      maMHInput.style.backgroundColor = "";
      maMHInput.value = "";
  }
  if(tenMHInput) {
      tenMHInput.disabled = true;
      tenMHInput.value = "";
  }
  selectedIndex = -1;
  if (formGrid) formGrid.style.display = "none";
  setButtonState("initial");

  render();
};

// ======================
// XÓA
// ======================
window.xoa = async function() {
  clearError();
  if (isThem || isSua) return showError("Đang trong chế độ Thêm/Sửa, không thể Xóa!");
  if (selectedIndex < 0) return showError("Vui lòng chọn một dòng để xóa!");

  var item = data[selectedIndex];

  try {
    // Kiểm tra xem môn học đó có được đăng ký hay không
    console.log(`Checking status for: /monhoc/${item.maMH}/check-status`);
    var checkRes = await fetch(`/monhoc/${item.maMH}/check-status`);
    console.log("Check response status:", checkRes.status);
    
    var checkData = await parseResponse(checkRes);
    console.log("Check data:", checkData);

    if (checkData.da_dangky_thi) {
      // Nếu đã được đăng ký, hiển thị thông báo
      console.log("Môn học đã được đăng ký, không cho xóa");
      showError("Môn này đã được đăng ký. Không thể xóa!");
      return;
    }

    // Nếu chưa được đăng ký, hiển thị dialog xác nhận
    console.log("Môn học chưa được đăng ký, hiển thị dialog");
    if(errorText) {
        errorText.innerHTML = `
          <div style="background:#fee2e2;padding:10px;border-radius:6px;">
            Ban co muon xoa mon hoc ${item.tenMH}?
            <br><br>
            <button onclick="thucHienXoa()">Xoa</button>
            <button onclick="huyXoa()">Huy</button>
          </div>
        `;
    }
  } catch (err) {
    console.error("Error in xoa:", err);
    showError(err.message);
  }
};

window.thucHienXoa = async function() {
  var item = data[selectedIndex];

  try {
    var res = await fetch(`/monhoc/${item.maMH}`, {
      method: "DELETE"
    });

    var resData = await parseResponse(res);

    stackUndo.push({ type: "DELETE", data: item, index: selectedIndex });
    data.splice(selectedIndex, 1);

    selectedIndex = -1;
    clearError();
    showSuccess(resData.message);
    if (formGrid) formGrid.style.display = "none";
    setButtonState("initial");

    if (selectedIndex === -1) setButtonState("initial");
    else setButtonState("default");
    render();

  } catch (err) {
    showError(err.message);
  }
};

window.huyXoa = function() {
  clearError();
  setState("Da huy xoa");
};

// ======================
// HỦY
// ======================
window.huy = function() {
  clearError();
  isSua = false;
  isThem = false;
  editingMa = null;

  if(maMHInput) {
      maMHInput.value = "";
      maMHInput.disabled = true;
      maMHInput.style.backgroundColor = "";
  }
  if(tenMHInput) {
      tenMHInput.value = "";
      tenMHInput.disabled = true;
  }

  selectedIndex = -1;
  if (formGrid) formGrid.style.display = "none";
  setButtonState("initial");
  render();
};

// ======================
// UNDO
// ======================
window.undo = async function() {
    clearError();
    if (isSua && selectedIndex >= 0) {
        var original = data[selectedIndex];
        if (tenMHInput) {
            tenMHInput.value = original.tenMH;
        }
        if (btnUndo) btnUndo.style.display = "none";
        return;
    }
};


// Real-time validation for duplicate subject code
if (maMHInput) {
    maMHInput.addEventListener('input', function() {
        if (!isThem) return;
        var val = this.value.trim().toUpperCase();
        if (!val) {
            clearError();
            if (btnGhi) { btnGhi.disabled = false; btnGhi.style.opacity = "1"; }
            return;
        }
        
        var exists = data.some(function(item) { 
            return item.maMH && item.maMH.trim().toUpperCase() === val; 
        });
        
        if (exists) {
            showError("Mã môn học đã tồn tại trong danh sách!");
            if (btnGhi) { btnGhi.disabled = true; btnGhi.style.opacity = "0.5"; btnGhi.style.cursor = "not-allowed"; }
        } else {
            clearError();
            if (btnGhi) { btnGhi.disabled = false; btnGhi.style.opacity = "1"; btnGhi.style.cursor = "pointer"; }
        }
    });
}

if (tenMHInput) {
    tenMHInput.addEventListener('input', function() {
        if (isSua && selectedIndex >= 0) {
            var original = data[selectedIndex];
            if (this.value.trim() !== (original.tenMH || "").trim()) {
                if (btnUndo) btnUndo.style.display = "inline-block";
            } else {
                if (btnUndo) btnUndo.style.display = "none";
            }
        }
    });
}

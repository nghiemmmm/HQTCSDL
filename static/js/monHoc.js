console.log("JS NEW VERSION LOADED");

// Chuyển toàn bộ let/const thành var để tránh lỗi khai báo lại khi load nhiều lần
var data = [];
var selectedIndex = -1;
var isSua = false;
var isThem = false;
var editingMa = null;
var stackUndo = [];

var maMHInput = document.getElementById("maMH");
var tenMHInput = document.getElementById("tenMH");
var searchTenMHInput = document.getElementById("searchTenMH");
var stateText = document.getElementById("stateText");
var errorText = document.getElementById("errorText");

var btnThem = document.getElementById("btnThem");
var btnSua = document.getElementById("btnSua");
var btnXoa = document.getElementById("btnXoa");
var btnGhi = document.getElementById("btnGhi");
var btnHuy = document.getElementById("btnHuy");
var btnUndo = document.getElementById("btnUndo");

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

// ======================
// HELPER
// ======================
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
    throw new Error(resData.detail || resData.message || "Lỗi không xác định");
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

  if (searchTenMHInput) {
    searchTenMHInput.addEventListener("input", () => {
      if (isSua) return;

      clearError();
      selectedIndex = -1;
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
function render() {
  var tbody = document.getElementById("tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  var keyword = searchTenMHInput ? searchTenMHInput.value.trim().toLowerCase() : "";

  data.forEach((item, index) => {
    if (keyword && !(item.tenMH || "").toLowerCase().includes(keyword)) return;

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
}

// ======================
// SELECT
// ======================
window.selectRow = function(index) {
  if (isSua || isThem) {
    showError("Vui lòng Ghi hoặc Hủy trước khi chọn môn khác!");
    return;
  }
  clearError();

  selectedIndex = index;
  if (maMHInput) maMHInput.value = data[index].maMH;
  if (tenMHInput) tenMHInput.value = data[index].tenMH;

  setState("Đang chọn: " + data[index].maMH);
  render();
};

// ======================
// VALIDATE
// ======================
function validate() {
  var ma = maMHInput ? maMHInput.value.trim() : "";
  var ten = tenMHInput ? tenMHInput.value.trim() : "";

  if (!ma || !ten) {
    showError("Vui lòng nhập đầy đủ Mã môn học và Tên môn học.");
    return false;
  }
  if (ma.length > 5) {
    showError("Mã môn học không được vượt quá 5 ký tự.");
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

  if(maMHInput) {
      maMHInput.disabled = false;
      maMHInput.style.backgroundColor = "";
      maMHInput.value = "";
      maMHInput.focus();
  }
  if(tenMHInput) {
      tenMHInput.disabled = false;
      tenMHInput.value = "";
  }

  render();
};

window.sua = function() {
  clearError();
  if (selectedIndex < 0) return showError("Vui lòng chọn dòng cần sửa");

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
      tenMHInput.focus();
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
  setButtonState("default");

  render();
};

// ======================
// XÓA
// ======================
window.xoa = function() {
  clearError();
  if (isThem || isSua) return showError("Đang trong chế độ Thêm/Sửa, không thể Xóa!");
  if (selectedIndex < 0) return showError("Vui lòng chọn một dòng để xóa!");

  var item = data[selectedIndex];

  if(errorText) {
      errorText.innerHTML = `
        <div style="background:#fee2e2;padding:10px;border-radius:6px;">
          Xóa ${item.tenMH}?
          <br><br>
          <button onclick="thucHienXoa()">Xóa</button>
          <button onclick="huyXoa()">Hủy</button>
        </div>
      `;
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

    render();

  } catch (err) {
    showError(err.message);
  }
};

window.huyXoa = function() {
  clearError();
  setState("Đã hủy xóa");
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
  setButtonState("default");
  render();
};

// ======================
// UNDO
// ======================
window.undo = async function() {
  clearError();
  if (isThem || isSua) return showError("Không thể undo lúc này");

  var action = stackUndo.pop();
  if (!action) return;

  try {
    if (action.type === "ADD") {
      var res = await fetch(`/monhoc/${action.data.mamh}`, { method: "DELETE" });
      var resData = await parseResponse(res);
      showSuccess("Undo: " + resData.message);
      data.pop();
    }

    if (action.type === "DELETE") {
      var res2 = await fetch("/monhoc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mamh: action.data.maMH,
          tenmh: action.data.tenMH
        })
      });

      var resData2 = await parseResponse(res2);
      showSuccess("Undo: " + resData2.message);

      data.push({ maMH: action.data.maMH, tenMH: action.data.tenMH });
    }

    if (action.type === "UPDATE") {
      var res3 = await fetch(`/monhoc/${action.new.maMH}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mamh: action.old.maMH,
          tenmh: action.old.tenMH
        })
      });

      var resData3 = await parseResponse(res3);
      showSuccess("Undo: " + resData3.message);

      data[action.index] = action.old;
    }

    render();

  } catch (err) {
    showError("Undo thất bại: " + err.message);
  }
};
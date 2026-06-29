let editingKey = null;
let registrations = [];

function shouldShowTeacherColumn() {
  return window.currentUser?.role !== "GIANGVIEN";
}

function tableColumnCount() {
  return shouldShowTeacherColumn() ? 9 : 8;
}

function clearErrors() {
  document.querySelectorAll('span[id$="Error"]').forEach(span => {
    span.classList.add('hidden');
    span.innerText = "";
  });
}

function showError(fieldId, message) {
  const errorSpan = document.getElementById(fieldId + "Error");
  if (errorSpan) {
    errorSpan.innerText = message;
    errorSpan.classList.remove('hidden');
  }
}

function placeholderOption(label) {
  return `<option value="" disabled selected hidden>${label}</option>`;
}

function setLoading(message) {
  const rows = document.getElementById("registrationRows");
  if (rows) rows.innerHTML = `<tr><td colspan="${tableColumnCount()}" class="empty-cell">${message}</td></tr>`;
}

function toInputDateTime(value) {
  if (!value) return "";
  const normalized = value.length === 10 ? `${value}T00:00` : value;
  return normalized.slice(0, 16);
}

function readFormData() {
  return {
    malop: document.getElementById("class").value.trim(),
    mamh: document.getElementById("subject").value.trim(),
    trinhdo: document.getElementById("level").value.trim(),
    lan: parseInt(document.getElementById("attempt").value, 10),
    ngaythi: document.getElementById("date").value.trim(),
    thoigian: parseInt(document.getElementById("duration").value, 10),
    socauthi: parseInt(document.getElementById("questionCount").value, 10),
    magv: ["GIANGVIEN", "PGV"].includes(window.currentUser?.role)
      ? (window.currentUser?.ma || "")
      : null
  };
}

function validateForm(data) {
  let hasError = false;
  if (!data.malop) { showError("class", "Vui long chon lop."); hasError = true; }
  if (!data.mamh) { showError("subject", "Vui long chon mon."); hasError = true; }
  if (!data.trinhdo) { showError("level", "Vui long chon trinh do."); hasError = true; }
  if (!data.lan) { showError("attempt", "Vui long chon lan thi."); hasError = true; }
  if (!data.ngaythi) { showError("date", "Vui long chon ngay gio thi."); hasError = true; }
  if (!data.thoigian || data.thoigian < 5 || data.thoigian > 60) {
    showError("duration", "Thoi gian thi phai tu 5 den 60 phut.");
    hasError = true;
  }
  if (!data.socauthi || data.socauthi < 10 || data.socauthi > 100) {
    showError("questionCount", "So cau hoi phai tu 10 den 100.");
    hasError = true;
  }
  return !hasError;
}

function sameExamRegistration(item, data, attempt) {
  return item.malop === data.malop
    && item.mamh === data.mamh
    && Number(item.lan) === attempt;
}

function validateAttemptSequence(data) {
  if (data.lan === 1) return true;

  if (data.lan !== 2) {
    showError("attempt", "Lan thi chi duoc la 1 hoac 2.");
    return false;
  }

  const firstAttempt = registrations.find(item => sameExamRegistration(item, data, 1));
  if (!firstAttempt) {
    showError("attempt", "Phai dang ky lich thi lan 1 truoc khi dang ky lan 2.");
    return false;
  }

  const firstDate = new Date(firstAttempt.ngaythi);
  const secondDate = new Date(data.ngaythi);
  firstDate.setHours(0, 0, 0, 0);
  secondDate.setHours(0, 0, 0, 0);

  if (secondDate <= firstDate) {
    showError("date", "Ngay thi lan 2 phai sau ngay thi lan 1 it nhat 1 ngay.");
    return false;
  }

  return true;
}

async function readError(response, fallback) {
  try {
    const text = await response.text();
    try {
      const data = JSON.parse(text);
      if (typeof data.detail === "string") return data.detail;
      if (data.detail && typeof data.detail.message === "string") return data.detail.message;
      if (Array.isArray(data.detail)) return data.detail.map(item => item.msg).join("; ");
      if (data.message) return data.message;
      return JSON.stringify(data) !== "{}" ? JSON.stringify(data) : fallback;
    } catch (e) {
      // If not JSON, it might be an HTML 500 error page or plain text
      console.error("Non-JSON error response:", text);
      return text.includes("Exception") || text.includes("Error") 
        ? "Lỗi hệ thống từ máy chủ (HTTP " + response.status + "). Chi tiết: " + text.substring(0, 100) + "..." 
        : fallback;
    }
  } catch (err) {
    return fallback;
  }
}

async function checkQuestionAvailability(data) {
  const params = new URLSearchParams({
    mamh: data.mamh,
    trinhdo: data.trinhdo,
    socauthi: String(data.socauthi)
  });
  const response = await fetch(`/dangkythi/check-cauhoi?${params.toString()}`);
  if (!response.ok) {
    throw new Error(await readError(
      response,
      "Không thể kiểm tra số câu hỏi trong bộ đề. Vui lòng kiểm tra lại môn học, trình độ và số câu thi."
    ));
  }
  const result = await response.json();
  if (!result.is_hop_le) {
    const message = result.thong_bao || "Không đủ câu hỏi trong bộ đề.";
    showError("questionCount", message);
    window.notify?.(message, "error");
    return false;
  }
  return true;
}

async function loadOptions() {
  const response = await fetch("/dangkythi/lophoc");
  if (!response.ok) throw new Error("Khong the tai danh sach lop");

  const classes = await response.json();
  const classSelect = document.getElementById("class");
  classSelect.innerHTML = placeholderOption("Chon lop");
  classes.forEach(lop => {
    const option = document.createElement("option");
    option.value = lop.malop;
    option.textContent = `${lop.malop} - ${lop.tenlop}`;
    classSelect.appendChild(option);
  });

  const subjectUrl = "/dangkythi/monhoc";
  const subjectResponse = await fetch(subjectUrl);
  if (!subjectResponse.ok) throw new Error("Khong the tai danh sach mon hoc");

  const subjects = await subjectResponse.json();
  const subjectSelect = document.getElementById("subject");
  subjectSelect.innerHTML = placeholderOption("Chon mon");
  subjects.forEach(mh => {
    const option = document.createElement("option");
    option.value = mh.mamh;
    option.textContent = mh.tenmh;
    subjectSelect.appendChild(option);
  });
}

async function loadRegistrations() {
  const keyword = document.getElementById("searchInput")?.value.trim() || "";
  const url = keyword ? `/dangkythi/api?keyword=${encodeURIComponent(keyword)}` : "/dangkythi/api";
  setLoading("Dang tai lich thi...");

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(await readError(response, "Khong the tai lich thi"));
    registrations = await response.json();
    renderRegistrations();
  } catch (error) {
    setLoading(error.message);
    window.notify?.(error.message, "error");
  }
}

function renderRegistrations() {
  const rows = document.getElementById("registrationRows");
  if (!rows) return;

  document.getElementById("teacherHeader")?.classList.toggle("hidden", !shouldShowTeacherColumn());

  if (!registrations.length) {
    rows.innerHTML = `<tr><td colspan="${tableColumnCount()}" class="empty-cell">Chua co lich thi phu hop.</td></tr>`;
    return;
  }

  rows.innerHTML = "";
  registrations.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.malop}</td>
      <td>${item.mamh}</td>
      <td>${item.lan}</td>
      <td>${item.trinhdo || ""}</td>
      <td>${item.ngaythi_text || ""}</td>
      <td>${item.socauthi || ""}</td>
      <td>${item.thoigian || ""} phut</td>
      ${shouldShowTeacherColumn() ? `<td>${item.magv || ""}</td>` : ""}
      <td class="row-actions">
        <button class="btn btn-outline btn-sm" type="button" data-action="edit" data-permission="update_exam_registration">Sua</button>
        <button class="btn btn-danger btn-sm" type="button" data-action="delete" data-permission="delete_exam_registration">Xoa</button>
      </td>
    `;
    const isPast = new Date(item.ngaythi) <= new Date();

    const editBtn = tr.querySelector('[data-action="edit"]');
    if (isPast) {
      editBtn.disabled = true;
      editBtn.title = "Lịch thi đã đến giờ hoặc đã qua, không được sửa";
      editBtn.style.opacity = "0.5";
      editBtn.style.cursor = "not-allowed";
    } else if (!window.hasPermission || window.hasPermission("update_exam_registration")) {
      editBtn.addEventListener("click", () => startEdit(item));
    } else {
      editBtn.remove();
    }

    const deleteBtn = tr.querySelector('[data-action="delete"]');
    if (isPast) {
      deleteBtn.disabled = true;
      deleteBtn.title = "Lịch thi đã đến giờ hoặc đã qua, không được xóa";
      deleteBtn.style.opacity = "0.5";
      deleteBtn.style.cursor = "not-allowed";
    } else if (!window.hasPermission || window.hasPermission("delete_exam_registration")) {
      deleteBtn.addEventListener("click", () => deleteRegistration(item));
    } else {
      deleteBtn.remove();
    }

    rows.appendChild(tr);
  });
}

function setKeyFieldsDisabled(disabled) {
  ["class", "subject", "attempt"].forEach(id => {
    const element = document.getElementById(id);
    element.disabled = disabled;
    element.classList.toggle("locked-field", disabled);
    element.title = disabled ? "Thong tin khoa lich thi, khong duoc sua" : "";
  });
}

function startEdit(item) {
  editingKey = { malop: item.malop, mamh: item.mamh, lan: item.lan };
  document.getElementById("class").value = item.malop;
  document.getElementById("subject").value = item.mamh;
  document.getElementById("level").value = item.trinhdo;
  document.getElementById("attempt").value = item.lan;
  document.getElementById("date").value = toInputDateTime(item.ngaythi);
  document.getElementById("duration").value = item.thoigian || "";
  document.getElementById("questionCount").value = item.socauthi || "";
  setKeyFieldsDisabled(true);
  document.getElementById("saveBtn").innerText = "Cap nhat";
  document.getElementById("cancelEditBtn").classList.remove("hidden");
}

function cancelEdit() {
  editingKey = null;
  document.getElementById("examForm").reset();
  setKeyFieldsDisabled(false);
  document.getElementById("saveBtn").innerText = "Ghi";
  document.getElementById("cancelEditBtn").classList.add("hidden");
  clearErrors();
}

async function deleteRegistration(item) {
  if (!confirm(`Xoa lich thi ${item.malop} - ${item.mamh} lan ${item.lan}?`)) return;
  try {
    const response = await fetch(`/dangkythi/${encodeURIComponent(item.malop)}/${encodeURIComponent(item.mamh)}/${item.lan}`, {
      method: "DELETE"
    });
    if (!response.ok) throw new Error(await readError(response, "Khong the xoa lich thi"));
    window.notify?.("Da xoa lich thi", "success");
    await loadRegistrations();
  } catch (error) {
    window.notify?.(error.message, "error");
  }
}

async function submitForm(event) {
  event.preventDefault();
  clearErrors();
  const data = readFormData();
  if (editingKey) {
    data.malop = editingKey.malop;
    data.mamh = editingKey.mamh;
    data.lan = editingKey.lan;
  }
  if (!validateForm(data)) return;
  if (!validateAttemptSequence(data)) return;
  try {
    if (!(await checkQuestionAvailability(data))) return;
  } catch (error) {
    showError("questionCount", error.message);
    window.notify?.(error.message, "error");
    return;
  }

  const url = editingKey
    ? `/dangkythi/${encodeURIComponent(editingKey.malop)}/${encodeURIComponent(editingKey.mamh)}/${editingKey.lan}`
    : "/dangkythi";
  const method = editingKey ? "PUT" : "POST";

  try {
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(await readError(response, "Khong the luu lich thi"));
    window.notify?.(editingKey ? "Da cap nhat lich thi" : "Da ghi lich thi thanh cong", "success");
    cancelEdit();
    await loadRegistrations();
  } catch (error) {
    window.notify?.(error.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const dateInput = document.getElementById("date");
  if (dateInput) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    
    const tzOffset = tomorrow.getTimezoneOffset() * 60000;
    const minLocalISO = new Date(tomorrow - tzOffset).toISOString().slice(0, 16);
    dateInput.min = minLocalISO;
    
    const maxDate = new Date(tomorrow);
    maxDate.setDate(maxDate.getDate() + 180);
    const maxLocalISO = new Date(maxDate - tzOffset).toISOString().slice(0, 16);
    dateInput.max = maxLocalISO;
  }

  const searchInput = document.getElementById("searchInput");
  if (searchInput && !shouldShowTeacherColumn()) {
    searchInput.placeholder = "Tim lop, mon";
  }

  document.getElementById("examForm")?.addEventListener("submit", submitForm);
  document.getElementById("cancelEditBtn")?.addEventListener("click", cancelEdit);
  document.getElementById("searchBtn")?.addEventListener("click", loadRegistrations);
  document.getElementById("reloadBtn")?.addEventListener("click", () => {
    document.getElementById("searchInput").value = "";
    loadRegistrations();
  });
  document.getElementById("searchInput")?.addEventListener("keydown", event => {
    if (event.key === "Enter") {
      event.preventDefault();
      loadRegistrations();
    }
  });

  try {
    await loadOptions();
    await loadRegistrations();
  } catch (error) {
    console.error(error);
    window.notify?.(error.message, "error");
    showError("class", "Khong the tai du lieu tu may chu.");
  }
});

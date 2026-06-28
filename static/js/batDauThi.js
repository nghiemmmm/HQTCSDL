let currentMaLop = "";
let currentExamInfo = null;
let selectedStudentSchedule = null;
const isPracticeUser = window.currentUser?.role === "GIANGVIEN";

async function readErrorMessage(response, fallback) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map(item => item.msg).join("; ");
    if (data.detail && typeof data.detail.message === "string") return data.detail.message;
    return data.message || fallback;
  } catch (error) {
    return fallback;
  }
}

function setExamDetailState(text) {
  document.getElementById("socauDisplay").innerText = text;
  document.getElementById("thoigianDisplay").innerText = text;
  document.getElementById("trinhdoDisplay").innerText = text;
  setExamDetailMessage("");
}

function setExamDetailMessage(message) {
  const element = document.getElementById("examDetailMessage");
  if (!element) return;
  element.innerText = message || "";
  element.hidden = !message;
}

function setStartButtonVisible(visible) {
  const button = document.querySelector(".startBtn");
  if (!button) return;
  button.hidden = !visible;
}

function placeholderOption(label) {
  return `<option value="" disabled selected hidden>${label}</option>`;
}

function setManualExamFieldsVisible(visible) {
  const monhocLabel = document.getElementById("monhocLabel");
  const monhocSelect = document.getElementById("monhocSelect");
  const manualRow = document.getElementById("manualExamFieldsRow");
  if (monhocLabel) monhocLabel.hidden = !visible;
  if (monhocSelect) monhocSelect.hidden = !visible;
  if (manualRow) manualRow.hidden = !visible;
}

function statusClass(status) {
  if (status === "Được thi hôm nay") return "is-open";
  if (status === "Chưa đến ngày thi") return "is-waiting";
  return "is-closed";
}

function renderScheduleSummary(schedule) {
  const element = document.getElementById("scheduleSummary");
  if (!element) return;
  if (!schedule) {
    element.hidden = true;
    element.innerHTML = "";
    return;
  }

  element.hidden = false;
  element.innerHTML = `
    <div class="summary-title">
      <span>${schedule.tenmh}</span>
      <span class="status-pill ${statusClass(schedule.trangthai)}">${schedule.trangthai}</span>
    </div>
    <div class="summary-grid">
      <div class="summary-item"><span>Mã môn</span><strong>${schedule.mamh}</strong></div>
      <div class="summary-item"><span>Lần thi</span><strong>${schedule.lan}</strong></div>
      <div class="summary-item"><span>Ngày thi</span><strong>${schedule.ngaythi_text}</strong></div>
      <div class="summary-item"><span>Thời gian</span><strong>${schedule.thoigian} phút</strong></div>
    </div>
  `;
}

function getExamAvailability(info) {
  if (!info || isPracticeUser) return { allowed: true, message: "" };

  if (Object.prototype.hasOwnProperty.call(info, "duoc_bat_dau_thi")) {
    return {
      allowed: Boolean(info.duoc_bat_dau_thi),
      state: info.trangthai || "Không được thi",
      message: info.duoc_bat_dau_thi ? "" : (info.trangthai || "Lịch thi chưa được phép bắt đầu.")
    };
  }

  const startAt = info.ngaythi ? new Date(info.ngaythi) : null;
  const durationMinutes = parseInt(info.thoigian, 10) || 0;
  if (!startAt || Number.isNaN(startAt.getTime()) || durationMinutes <= 0) {
    return { allowed: false, state: "L\u1ed7i", message: "L\u1ecbch thi ch\u01b0a c\u00f3 th\u1eddi gian h\u1ee3p l\u1ec7." };
  }

  const now = new Date();
  const endAt = new Date(startAt.getTime() + durationMinutes * 60000);
  if (now < startAt) {
    return {
      allowed: false,
      state: "Ch\u01b0a t\u1edbi gi\u1edd",
      message: `Ch\u01b0a \u0111\u1ebfn gi\u1edd thi. B\u1eaft \u0111\u1ea7u l\u00fac ${startAt.toLocaleString("vi-VN")}.`
    };
  }
  if (now > endAt) {
    return {
      allowed: false,
      state: "B\u00e0i thi \u0111\u00e3 h\u1ebft th\u1eddi gian l\u00e0m b\u00e0i",
      message: `\u0110\u00e3 h\u1ebft gi\u1edd v\u00e0o thi. K\u1ebft th\u00fac l\u00fac ${endAt.toLocaleString("vi-VN")}.`
    };
  }
  return { allowed: true, state: "S\u1eb5n s\u00e0ng", message: "" };
}

function validateExamConfig(showMessage = false) {
  const monhoc = document.getElementById("monhocSelect").value;
  const ngaythi = document.getElementById("ngaythiInput").value;
  const lanthi = document.getElementById("lanthiSelect").value;

  if (!monhoc) {
    if (showMessage) window.notify?.("Vui lòng chọn môn học", "warning");
    return false;
  }

  if (!ngaythi) {
    if (showMessage) window.notify?.("Vui lòng chọn ngày thi", "warning");
    return false;
  }

  if (!lanthi) {
    if (showMessage) window.notify?.("Vui lòng chọn lần thi", "warning");
    return false;
  }

  if (!currentMaLop) {
    if (showMessage) window.notify?.("Vui lòng chọn lớp thi", "error");
    return false;
  }

  return true;
}

async function handleExamDetailError(response) {
  const fallbackByStatus = {
    401: "Phi\u00ean \u0111\u0103ng nh\u1eadp h\u1ebft h\u1ea1n. Vui l\u00f2ng \u0111\u0103ng nh\u1eadp l\u1ea1i.",
    403: "B\u1ea1n kh\u00f4ng c\u00f3 quy\u1ec1n xem th\u00f4ng tin thi n\u00e0y.",
    404: "Kh\u00f4ng t\u00ecm th\u1ea5y l\u1ecbch thi ph\u00f9 h\u1ee3p.",
    422: "Th\u00f4ng tin m\u00f4n, ng\u00e0y thi ho\u1eb7c l\u1ea7n thi kh\u00f4ng h\u1ee3p l\u1ec7.",
    500: "L\u1ed7i m\u00e1y ch\u1ee7 khi l\u1ea5y th\u00f4ng tin thi."
  };

  const message = await readErrorMessage(
    response,
    fallbackByStatus[response.status] || "Kh\u00f4ng th\u1ec3 l\u1ea5y th\u00f4ng tin thi."
  );

  setExamDetailState(response.status === 404 ? "Kh\u00f4ng c\u00f3 l\u1ecbch" : "L\u1ed7i");
  window.notify?.(message, "error");

  if (response.status === 401) {
    setTimeout(() => {
      window.location.href = "/user/login";
    }, 1200);
  }
}

async function loadClassForStudent(userCode) {
  const res = await fetch(`/thi/nhanLop?masv=${encodeURIComponent(userCode)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });

  if (!res.ok) {
    document.getElementById("className").innerText = "Không tìm thấy lớp";
    document.getElementById("classCode").innerText = "Mã lớp: N/A";
    return;
  }

  const classInfo = await res.json();
  currentMaLop = classInfo.malop.trim();
  document.getElementById("className").innerText = classInfo.tenlop;
  document.getElementById("classCode").innerText = `Mã lớp: ${currentMaLop}`;
  document.getElementById("studentInfo").innerText = `Mã sinh viên: ${userCode}`;
}

async function loadClassChooserForTeacher() {
  // Show the schedule select like students, hide manual fields initially
  const scheduleLabel = document.getElementById("lichThiLabel");
  const scheduleSelect = document.getElementById("lichThiSelect");
  const lopLabel = document.getElementById("lopThiLabel");
  const lopSelect = document.getElementById("lopThiSelect");

  if (scheduleLabel) { scheduleLabel.hidden = false; scheduleLabel.innerText = "Kỳ thi đã đăng ký"; }
  if (lopLabel) lopLabel.hidden = true;
  if (lopSelect) lopSelect.hidden = true;
  setManualExamFieldsVisible(false);
  setStartButtonVisible(false);

  document.getElementById("studentInfo").innerText = `Giảng viên thi thử: ${window.currentUser?.ma || ""}`;
  document.getElementById("className").innerText = "";
  document.getElementById("classCode").innerText = "";

  if (!scheduleSelect) return;

  scheduleSelect.hidden = false;
  scheduleSelect.innerHTML = placeholderOption("Đang tải kỳ thi...");

  const response = await fetch("/thi/api/danh-sach-ky-thi-gv");
  if (!response.ok) throw new Error("Không thể tải danh sách kỳ thi đã đăng ký");

  const data = await response.json();
  const registrations = data.registrations || [];

  scheduleSelect.innerHTML = placeholderOption(
    registrations.length ? "Chọn kỳ thi" : "Chưa có kỳ thi nào đăng ký"
  );

  registrations.forEach((reg, index) => {
    const opt = document.createElement("option");
    opt.value = String(index);
    opt.textContent = `${reg.tenmh} (${reg.mamh}) — ${reg.tenlop} — Lần ${reg.lan} — 📅 ${reg.ngaythi}`;
    scheduleSelect.appendChild(opt);
  });

  scheduleSelect.addEventListener("change", () => {
    const reg = registrations[Number(scheduleSelect.value)];
    if (!reg) return;

    // Auto-fill hidden fields
    currentMaLop = reg.malop.trim();
    document.getElementById("className").innerText = reg.tenlop;
    document.getElementById("classCode").innerText = `Mã lớp: ${currentMaLop}`;

    // Populate monhocSelect with the selected subject
    const monhocSelect = document.getElementById("monhocSelect");
    monhocSelect.innerHTML = "";
    const subjectOption = document.createElement("option");
    subjectOption.value = reg.mamh.trim();
    subjectOption.textContent = `${reg.mamh.trim()} - ${reg.tenmh}`;
    subjectOption.selected = true;
    monhocSelect.appendChild(subjectOption);

    // Fill ngaythi and lanthi
    const ngaythiInput = document.getElementById("ngaythiInput");
    const lanthiSelect = document.getElementById("lanthiSelect");
    ngaythiInput.value = reg.ngaythi_sort ? reg.ngaythi_sort.slice(0, 10) : "";
    lanthiSelect.value = String(reg.lan);

    // Show summary card like students
    renderScheduleSummary({
      tenmh: reg.tenmh,
      mamh: reg.mamh,
      lan: reg.lan,
      ngaythi_text: reg.ngaythi,
      thoigian: "...",
      trangthai: "Thi thử (giảng viên)",
    });

    setStartButtonVisible(true);
    fetchExamDetails();
  });

  if (!registrations.length) {
    setExamDetailState("Không có lịch");
    setExamDetailMessage("Bạn chưa đăng ký kỳ thi nào.");
    setStartButtonVisible(false);
    renderScheduleSummary(null);
  }
}

function setStudentScheduleFields(schedule) {
  const monhocSelect = document.getElementById("monhocSelect");
  const ngaythiInput = document.getElementById("ngaythiInput");
  const lanthiSelect = document.getElementById("lanthiSelect");
  const examDate = schedule.ngaythi ? schedule.ngaythi.slice(0, 10) : "";

  monhocSelect.innerHTML = "";
  const subjectOption = document.createElement("option");
  subjectOption.value = schedule.mamh;
  subjectOption.textContent = `${schedule.mamh} - ${schedule.tenmh}`;
  subjectOption.selected = true;
  monhocSelect.appendChild(subjectOption);

  ngaythiInput.value = examDate;
  lanthiSelect.value = String(schedule.lan);
  currentMaLop = schedule.malop || currentMaLop;
}

function showScheduleDetail(schedule, trinhdo = "...") {
  document.getElementById("socauDisplay").innerText = schedule.socauthi || "...";
  document.getElementById("thoigianDisplay").innerText = schedule.thoigian
    ? `${schedule.thoigian} phút`
    : "...";
  document.getElementById("trinhdoDisplay").innerText = trinhdo || "...";
}

function setStudentManualFieldsLocked(locked) {
  document.getElementById("monhocSelect").disabled = locked;
  document.getElementById("ngaythiInput").disabled = locked;
  document.getElementById("lanthiSelect").disabled = locked;
}

async function loadStudentSchedules() {
  setManualExamFieldsVisible(false);
  setStartButtonVisible(false);
  const scheduleLabel = document.getElementById("lichThiLabel");
  const scheduleSelect = document.getElementById("lichThiSelect");
  if (scheduleLabel) scheduleLabel.hidden = false;
  if (!scheduleSelect) return;

  setStudentManualFieldsLocked(true);
  const response = await fetch("/thi/lich-thi-cua-toi");
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Không thể tải lịch thi của sinh viên"));
  }

  const schedules = await response.json();
  scheduleSelect.innerHTML = placeholderOption(
    schedules.length ? "Chọn lịch thi" : "Không có lịch thi"
  );

  schedules.forEach((schedule, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `${schedule.tenmh} - Lần ${schedule.lan} - ${schedule.trangthai}`;
    scheduleSelect.appendChild(option);
  });

  scheduleSelect.addEventListener("change", () => {
    selectedStudentSchedule = schedules[Number(scheduleSelect.value)];
    if (!selectedStudentSchedule) return;
    setStudentScheduleFields(selectedStudentSchedule);
    renderScheduleSummary(selectedStudentSchedule);
    showScheduleDetail(selectedStudentSchedule);
    setStartButtonVisible(Boolean(selectedStudentSchedule.duoc_bat_dau_thi));
    setExamDetailMessage(
      selectedStudentSchedule.duoc_bat_dau_thi
        ? ""
        : selectedStudentSchedule.trangthai
    );
    fetchExamDetails();
  });

  if (!schedules.length) {
    setExamDetailState("Không có lịch");
    setExamDetailMessage("Lớp của bạn hiện chưa có lịch thi nào được đăng ký.");
    setStartButtonVisible(false);
    renderScheduleSummary(null);
  }
}

async function loadSubjects() {
  const resMonHoc = await fetch('/thi/monhoc-duoc-thi');
  if (!resMonHoc.ok) {
    window.notify?.("Không thể tải danh sách môn thi", "error");
    return;
  }

  const subjects = await resMonHoc.json();
  const monhocSelect = document.getElementById("monhocSelect");
  monhocSelect.innerHTML = placeholderOption("Ch\u1ecdn m\u00f4n h\u1ecdc");
  subjects.forEach(mh => {
    const option = document.createElement("option");
    option.value = mh.mamh;
    option.textContent = mh.tenmh;
    monhocSelect.appendChild(option);
  });
}

(async () => {
  const userCode = window.currentUser?.ma;

  if (!userCode) {
    document.getElementById("className").innerText = "Không tìm thấy thông tin đăng nhập";
    document.getElementById("classCode").innerText = "Mã lớp: N/A";
    return;
  }

  try {
    if (isPracticeUser) {
      await loadClassChooserForTeacher();
    } else {
      await loadClassForStudent(userCode);
      await loadStudentSchedules();
    }
  } catch (error) {
    console.error("Lỗi:", error);
    document.getElementById("className").innerText = "Lỗi kết nối máy chủ";
    window.notify?.(error.message || "Lỗi kết nối máy chủ", "error");
  }
})();
async function fetchExamDetails() {
  const monhoc = document.getElementById("monhocSelect").value;
  const ngaythi = document.getElementById("ngaythiInput").value;
  const lanthi = document.getElementById("lanthiSelect").value;

  if (!validateExamConfig(false)) {
    currentExamInfo = null;
    setExamDetailState("...");
    return;
  }

  try {
    const params = new URLSearchParams({
      mamonhoc: monhoc,
      lanthi,
      malop: currentMaLop,
      ngaythi
    });

    const res = await fetch(`/thi/layTTThi?${params.toString()}`);
    if (res.ok) {
      const info = await res.json();
      currentExamInfo = selectedStudentSchedule
        ? { ...info, ...selectedStudentSchedule }
        : info;
      const availability = getExamAvailability(currentExamInfo);
      document.getElementById("socauDisplay").innerText = info.socauthi;
      document.getElementById("thoigianDisplay").innerText = `${info.thoigian} phút`;
      document.getElementById("trinhdoDisplay").innerText = info.trinhdo;
      setStartButtonVisible(availability.allowed);
      if (!availability.allowed) {
        setExamDetailMessage(availability.message || availability.state);
        window.notify?.(availability.message, "warning");
        return;
      }
      setExamDetailMessage(info.active_session_message || "");
    } else {
      currentExamInfo = null;
      setStartButtonVisible(false);
      await handleExamDetailError(res);
    }
  } catch (error) {
    console.error("Lỗi lấy thông tin thi:", error);
    setExamDetailState("Lỗi");
    setStartButtonVisible(false);
    window.notify?.("Lỗi kết nối máy chủ khi lấy thông tin thi.", "error");
  }
}

document.getElementById("monhocSelect").addEventListener("change", fetchExamDetails);
document.getElementById("ngaythiInput").addEventListener("change", fetchExamDetails);
document.getElementById("lanthiSelect").addEventListener("change", fetchExamDetails);

document.querySelector(".startBtn")?.addEventListener("click", () => {
  const monhoc = document.getElementById("monhocSelect").value;
  const ngaythi = document.getElementById("ngaythiInput").value;
  const lanthi = document.getElementById("lanthiSelect").value;
  const socau = document.getElementById("socauDisplay").innerText;
  const thoigian = document.getElementById("thoigianDisplay").innerText;
  const trinhdo = document.getElementById("trinhdoDisplay").innerText;

  if (!validateExamConfig(true)) {
    return;
  }

  const unavailableStates = [
    "...",
    "L\u1ed7i",
    "Kh\u00f4ng c\u00f3 l\u1ecbch",
    "Ch\u01b0a t\u1edbi gi\u1edd",
    "B\u00e0i thi \u0111\u00e3 h\u1ebft th\u1eddi gian l\u00e0m b\u00e0i"
  ];
  const availability = getExamAvailability(currentExamInfo);
  if (unavailableStates.includes(socau) || !availability.allowed) {
    window.notify?.(availability.message || "L\u1ecbch thi kh\u00f4ng t\u1ed3n t\u1ea1i ho\u1eb7c kh\u00f4ng h\u1ee3p l\u1ec7!", "error");
    return;
  }

  const params = new URLSearchParams({
    mamonhoc: monhoc,
    lanthi: lanthi,
    malop: currentMaLop,
    ngaythi: ngaythi,
    socau: socau,
    thoigian: thoigian.replace(" phut", "").replace(" phút", "").trim(),
    trinhdo: trinhdo
  });
  window.location.href = `/thi/lam-bai?${params.toString()}`;
});

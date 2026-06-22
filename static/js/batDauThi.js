let currentMaLop = "";
const isPracticeUser = window.currentUser?.role !== "SINHVIEN";

async function readErrorMessage(response, fallback) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map(item => item.msg).join("; ");
    return data.message || fallback;
  } catch (error) {
    return fallback;
  }
}

function setExamDetailState(text) {
  document.getElementById("socauDisplay").innerText = text;
  document.getElementById("thoigianDisplay").innerText = text;
  document.getElementById("trinhdoDisplay").innerText = text;
}

function placeholderOption(label) {
  return `<option value="" disabled selected hidden>${label}</option>`;
}

function validateExamConfig(showMessage = false) {
  const monhoc = document.getElementById("monhocSelect").value;
  const ngaythi = document.getElementById("ngaythiInput").value;
  const lanthi = document.getElementById("lanthiSelect").value;

  if (!monhoc) {
    if (showMessage) window.notify?.("Vui long chon mon hoc", "warning");
    return false;
  }

  if (!ngaythi) {
    if (showMessage) window.notify?.("Vui long chon ngay thi", "warning");
    return false;
  }

  if (!lanthi) {
    if (showMessage) window.notify?.("Vui long chon lan thi", "warning");
    return false;
  }

  if (!currentMaLop) {
    if (showMessage) window.notify?.("Vui long chon lop thi", "error");
    return false;
  }

  return true;
}

async function handleExamDetailError(response) {
  const fallbackByStatus = {
    401: "Phien dang nhap het han. Vui long dang nhap lai.",
    403: "Ban khong co quyen xem thong tin thi nay.",
    404: "Khong tim thay lich thi phu hop.",
    422: "Thong tin mon, ngay thi hoac lan thi khong hop le.",
    500: "Loi may chu khi lay thong tin thi."
  };

  const message = await readErrorMessage(
    response,
    fallbackByStatus[response.status] || "Khong the lay thong tin thi."
  );

  setExamDetailState(response.status === 404 ? "Khong co lich" : "Loi");
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
    document.getElementById("className").innerText = "Khong tim thay lop";
    document.getElementById("classCode").innerText = "Ma lop: N/A";
    return;
  }

  const classInfo = await res.json();
  currentMaLop = classInfo.malop.trim();
  document.getElementById("className").innerText = classInfo.tenlop;
  document.getElementById("classCode").innerText = `Ma lop: ${currentMaLop}`;
  document.getElementById("studentInfo").innerText = `Ma sinh vien: ${userCode}`;
}

async function loadClassChooserForTeacher() {
  const label = document.getElementById("lopThiLabel");
  const select = document.getElementById("lopThiSelect");
  if (label) label.hidden = false;
  if (select) select.hidden = false;

  document.getElementById("studentInfo").innerText = `Giang vien thi thu: ${window.currentUser?.ma || ""}`;
  document.getElementById("className").innerText = "Chon lop thi thu";
  document.getElementById("classCode").innerText = "Ma lop: Chua chon";

  const response = await fetch("/dangkythi/lophoc");
  if (!response.ok) throw new Error("Khong the tai danh sach lop thi");

  const classes = await response.json();
  select.innerHTML = placeholderOption("Chon lop thi");
  classes.forEach(item => {
    const option = document.createElement("option");
    option.value = item.malop;
    option.textContent = `${item.malop} - ${item.tenlop}`;
    select.appendChild(option);
  });

  select.addEventListener("change", () => {
    currentMaLop = select.value;
    const selected = classes.find(item => item.malop === currentMaLop);
    document.getElementById("className").innerText = selected?.tenlop || "Lop thi thu";
    document.getElementById("classCode").innerText = `Ma lop: ${currentMaLop}`;
    fetchExamDetails();
  });
}

async function loadSubjects() {
  const resMonHoc = await fetch('/thi/monhoc-duoc-thi');
  if (!resMonHoc.ok) {
    window.notify?.("Khong the tai danh sach mon thi", "error");
    return;
  }

  const subjects = await resMonHoc.json();
  const monhocSelect = document.getElementById("monhocSelect");
  monhocSelect.innerHTML = placeholderOption("Chon mon hoc");
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
    document.getElementById("className").innerText = "Khong tim thay thong tin dang nhap";
    document.getElementById("classCode").innerText = "Ma lop: N/A";
    return;
  }

  try {
    if (isPracticeUser) {
      await loadClassChooserForTeacher();
    } else {
      await loadClassForStudent(userCode);
    }
    await loadSubjects();
  } catch (error) {
    console.error("Loi:", error);
    document.getElementById("className").innerText = "Loi ket noi may chu";
    window.notify?.(error.message || "Loi ket noi may chu", "error");
  }
})();
async function fetchExamDetails() {
  const monhoc = document.getElementById("monhocSelect").value;
  const ngaythi = document.getElementById("ngaythiInput").value;
  const lanthi = document.getElementById("lanthiSelect").value;

  if (!validateExamConfig(false)) {
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
      document.getElementById("socauDisplay").innerText = info.socauthi;
      document.getElementById("thoigianDisplay").innerText = `${info.thoigian} phut`;
      document.getElementById("trinhdoDisplay").innerText = info.trinhdo;
    } else {
      await handleExamDetailError(res);
    }
  } catch (error) {
    console.error("Loi lay thong tin thi:", error);
    setExamDetailState("Loi");
    window.notify?.("Loi ket noi may chu khi lay thong tin thi.", "error");
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

  if (socau === "..." || socau === "Lỗi" || socau === "Khong co lich" || socau === "Loi") {
    window.notify?.("Lịch thi không tồn tại hoặc không hợp lệ!", "error");
    return;
  }

  // Chuyển hướng sang phòng thi với các tham số cấu hình
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

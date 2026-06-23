let currentMaLop = "";
let currentExamInfo = null;
const isPracticeUser = window.currentUser?.role === "GIANGVIEN";

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

function getExamAvailability(info) {
  if (!info || isPracticeUser) return { allowed: true, message: "" };

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
      state: "H\u1ebft gi\u1edd",
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
    if (showMessage) window.notify?.("Vui l\u00f2ng ch\u1ecdn m\u00f4n h\u1ecdc", "warning");
    return false;
  }

  if (!ngaythi) {
    if (showMessage) window.notify?.("Vui l\u00f2ng ch\u1ecdn ng\u00e0y thi", "warning");
    return false;
  }

  if (!lanthi) {
    if (showMessage) window.notify?.("Vui l\u00f2ng ch\u1ecdn l\u1ea7n thi", "warning");
    return false;
  }

  if (!currentMaLop) {
    if (showMessage) window.notify?.("Vui l\u00f2ng ch\u1ecdn l\u1edbp thi", "error");
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
    document.getElementById("className").innerText = "Kh\u00f4ng t\u00ecm th\u1ea5y l\u1edbp";
    document.getElementById("classCode").innerText = "M\u00e3 l\u1edbp: N/A";
    return;
  }

  const classInfo = await res.json();
  currentMaLop = classInfo.malop.trim();
  document.getElementById("className").innerText = classInfo.tenlop;
  document.getElementById("classCode").innerText = `M\u00e3 l\u1edbp: ${currentMaLop}`;
  document.getElementById("studentInfo").innerText = `M\u00e3 sinh vi\u00ean: ${userCode}`;
}

async function loadClassChooserForTeacher() {
  const label = document.getElementById("lopThiLabel");
  const select = document.getElementById("lopThiSelect");
  if (label) label.hidden = false;
  if (select) select.hidden = false;

  document.getElementById("studentInfo").innerText = `Gi\u1ea3ng vi\u00ean thi th\u1eed: ${window.currentUser?.ma || ""}`;
  document.getElementById("className").innerText = "";
  document.getElementById("classCode").innerText = "";

  const response = await fetch("/thi/lophoc-duoc-thi");
  if (!response.ok) throw new Error("Không thể tải danh sách lớp thi");

  const classes = await response.json();
  select.innerHTML = placeholderOption("Ch\u1ecdn l\u1edbp thi");
  classes.forEach(item => {
    const option = document.createElement("option");
    option.value = item.malop;
    option.textContent = `${item.malop} - ${item.tenlop}`;
    select.appendChild(option);
  });

  select.addEventListener("change", () => {
    currentMaLop = select.value;
    const selected = classes.find(item => item.malop === currentMaLop);
    document.getElementById("className").innerText = selected?.tenlop || "L\u1edbp thi th\u1eed";
    document.getElementById("classCode").innerText = `M\u00e3 l\u1edbp: ${currentMaLop}`;
    fetchExamDetails();
  });
}

async function loadSubjects() {
  const resMonHoc = await fetch('/thi/monhoc-duoc-thi');
  if (!resMonHoc.ok) {
    window.notify?.("Kh\u00f4ng th\u1ec3 t\u1ea3i danh s\u00e1ch m\u00f4n thi", "error");
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
    document.getElementById("className").innerText = "Kh\u00f4ng t\u00ecm th\u1ea5y th\u00f4ng tin \u0111\u0103ng nh\u1eadp";
    document.getElementById("classCode").innerText = "M\u00e3 l\u1edbp: N/A";
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
    document.getElementById("className").innerText = "L\u1ed7i k\u1ebft n\u1ed1i m\u00e1y ch\u1ee7";
    window.notify?.(error.message || "L\u1ed7i k\u1ebft n\u1ed1i m\u00e1y ch\u1ee7", "error");
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
      currentExamInfo = info;
      const availability = getExamAvailability(info);
      if (!availability.allowed) {
        setExamDetailState(availability.state);
        window.notify?.(availability.message, "warning");
        return;
      }
      document.getElementById("socauDisplay").innerText = info.socauthi;
      document.getElementById("thoigianDisplay").innerText = `${info.thoigian} ph\u00fat`;
      document.getElementById("trinhdoDisplay").innerText = info.trinhdo;
    } else {
      currentExamInfo = null;
      await handleExamDetailError(res);
    }
  } catch (error) {
    console.error("L\u1ed7i l\u1ea5y th\u00f4ng tin thi:", error);
    setExamDetailState("L\u1ed7i");
    window.notify?.("L\u1ed7i k\u1ebft n\u1ed1i m\u00e1y ch\u1ee7 khi l\u1ea5y th\u00f4ng tin thi.", "error");
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

  const unavailableStates = ["...", "L\u1ed7i", "Kh\u00f4ng c\u00f3 l\u1ecbch", "L\u1ed7i", "Ch\u01b0a t\u1edbi gi\u1edd", "H\u1ebft gi\u1edd"];
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

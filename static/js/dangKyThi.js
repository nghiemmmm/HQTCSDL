function clearErrors() {
  const errorSpans = document.querySelectorAll('span[id$="Error"]');
  errorSpans.forEach(span => {
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

// Load danh sách lớp khi trang vừa tải xong
document.addEventListener("DOMContentLoaded", async function() {
  try {
    const response = await fetch("/lop/lophoc");
    if (!response.ok) throw new Error("Lỗi khi tải danh sách lớp");
    
    const classes = await response.json();
    const classSelect = document.getElementById("class");
    
    // Giữ lại option mặc định đầu tiên
    classSelect.innerHTML = placeholderOption("Chon lop");
    
    classes.forEach(lop => {
      const option = document.createElement("option");
      option.value = lop.malop;
      option.textContent = lop.malop + " - " + lop.tenlop;
      classSelect.appendChild(option);
    });

    // Tải danh sách môn học theo magv (Giả sử mặc định là GV01, anh/chị tự thay thế bằng magv đang đăng nhập)
    const magv = window.currentUser?.ma || "";
    const subjectUrl = window.currentUser?.role === "GIANGVIEN"
      ? `/dangkythi/monhocdk?magv=${encodeURIComponent(magv)}`
      : "/monhoc/danhsachMH";
    const resMonHoc = await fetch(subjectUrl);
    if (!resMonHoc.ok) throw new Error("Lỗi khi tải danh sách môn học");

    const subjects = await resMonHoc.json();
    const subjectSelect = document.getElementById("subject");
    subjectSelect.innerHTML = placeholderOption("Chon mon");
    subjects.forEach(mh => {
      const option = document.createElement("option");
      option.value = mh.mamh;
      option.textContent = mh.mamh + " - " + mh.tenmh;
      subjectSelect.appendChild(option);
    });

  } catch (error) {
    console.error("Lỗi:", error);
    showError("class", "Không thể tải danh sách dữ liệu từ máy chủ.");
  }
});

document.getElementById("examForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  clearErrors();

  const classId = document.getElementById("class").value.trim();
  const subjectId = document.getElementById("subject").value.trim();
  const level = document.getElementById("level").value.trim();
  const attempt = document.getElementById("attempt").value.trim();
  const date = document.getElementById("date").value.trim();
  const duration = document.getElementById("duration").value.trim();
  const questionCount = document.getElementById("questionCount").value.trim();

  let hasError = false;

  if (!classId) { showError("class", "Vui lòng chọn lớp."); hasError = true; }
  if (!subjectId) { showError("subject", "Vui lòng chọn môn."); hasError = true; }
  if (!level) { showError("level", "Vui lòng chọn trình độ."); hasError = true; }
  if (!attempt) { showError("attempt", "Vui lòng chọn lần thi."); hasError = true; }
  if (!date) { showError("date", "Vui lòng chọn ngày thi."); hasError = true; }
  
  if (!duration) { 
    showError("duration", "Vui lòng nhập thời gian."); 
    hasError = true; 
  } else {
    const durationNum = parseInt(duration, 10);
    if (isNaN(durationNum) || durationNum < 5 || durationNum > 60) {
      showError("duration", "Thời gian thi phải từ 5 đến 60 phút.");
      hasError = true;
    }
  }

  if (!questionCount) { 
    showError("questionCount", "Vui lòng nhập số câu."); 
    hasError = true; 
  } else {
    const questionCountNum = parseInt(questionCount, 10);
    if (isNaN(questionCountNum) || questionCountNum < 10 || questionCountNum > 100) {
      showError("questionCount", "So cau hoi phai tu 10 den 100.");
      hasError = true;
    }
  }

  if (hasError) return;

  const data = {
    malop: classId,
    mamh: subjectId,
    trinhdo: level,
    lan: parseInt(attempt, 10),
    ngaythi: date, // Pydantic sẽ tự động parse string 'YYYY-MM-DD' sang datetime
    thoigian: parseInt(duration, 10),
    socauthi: parseInt(questionCount, 10),
    magv: window.currentUser?.role === "GIANGVIEN" ? (window.currentUser?.ma || "") : null
  };

  console.log("Submit:", data);
  try {
    const response = await fetch("/dangkythi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Khong the tao lich thi");
    }

    window.notify?.("Da ghi lich thi thanh cong", "success");
    e.target.reset();
  } catch (error) {
    window.notify?.(error.message, "error");
  }
});

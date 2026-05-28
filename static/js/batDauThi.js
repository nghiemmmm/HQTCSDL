let currentMaLop = "";

(async () => {
  const masv = "001"; // Mặc định ban đầu
  try {
    const res = await fetch(`/thi/nhanLop?masv=${masv}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (res.ok) {
      const classInfo = await res.json();
      currentMaLop = classInfo.malop.trim();
      document.getElementById("className").innerText = classInfo.tenlop;
      document.getElementById("classCode").innerText = `Mã lớp: ${currentMaLop}`;
      document.getElementById("studentInfo").innerText = `Mã sinh viên: ${masv}`;
    } else {
      document.getElementById("className").innerText = "Không tìm thấy lớp";
      document.getElementById("classCode").innerText = "Mã lớp: N/A";
    }

    // Tải danh sách môn học
    const resMonHoc = await fetch('/monhoc/monhoc');
    if (resMonHoc.ok) {
      const subjects = await resMonHoc.json();
      const monhocSelect = document.getElementById("monhocSelect");
      subjects.forEach(mh => {
        const option = document.createElement("option");
        option.value = mh.mamh;
        option.textContent = mh.tenmh;
        monhocSelect.appendChild(option);
      });
    } else {
      console.error("Không thể tải danh sách môn học");
    }

  } catch (error) {
    console.error("Lỗi:", error);
    document.getElementById("className").innerText = "Lỗi kết nối máy chủ";
  }
})();

async function fetchExamDetails() {
  const monhoc = document.getElementById("monhocSelect").value;
  const ngaythi = document.getElementById("ngaythiInput").value;
  const lanthi = document.getElementById("lanthiSelect").value;

  if (!monhoc || !ngaythi || !lanthi || !currentMaLop) {
    document.getElementById("socauDisplay").innerText = "...";
    document.getElementById("thoigianDisplay").innerText = "...";
    document.getElementById("trinhdoDisplay").innerText = "...";
    return;
  }

  try {
    const res = await fetch(`/thi/layTTThi?mamonhoc=${monhoc}&lanthi=${lanthi}&malop=${currentMaLop}&ngaythi=${ngaythi}`);
    if (res.ok) {
      const info = await res.json();
      document.getElementById("socauDisplay").innerText = info.socauthi;
      document.getElementById("thoigianDisplay").innerText = info.thoigian + " phút";
      document.getElementById("trinhdoDisplay").innerText = info.trinhdo;
    } else {
      document.getElementById("socauDisplay").innerText = "Lỗi/Trống";
      document.getElementById("thoigianDisplay").innerText = "Lỗi/Trống";
      document.getElementById("trinhdoDisplay").innerText = "Lỗi/Trống";
    }
  } catch (error) {
    console.error("Lỗi lấy thông tin thi:", error);
  }
}

document.getElementById("monhocSelect").addEventListener("change", fetchExamDetails);
document.getElementById("ngaythiInput").addEventListener("change", fetchExamDetails);
document.getElementById("lanthiSelect").addEventListener("change", fetchExamDetails);

const menuBtn = document.getElementById("menuBtn");
const mobileNav = document.getElementById("mobileNav");

menuBtn.onclick = () => {
  mobileNav.classList.toggle("hidden");
};

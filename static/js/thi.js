const urlParams = new URLSearchParams(window.location.search);
const maMH = urlParams.get("mamonhoc") || "";
const lanThi = urlParams.get("lanthi") || "";
const maLop = urlParams.get("malop") || "";
const ngayThi = urlParams.get("ngaythi") || "";

let QUESTIONS = [];
let currentIdx = 0;
let answers = {};
let flagged = new Set();
let timeLeft = 0;
let timerId = null;

function setText(id, text) {
  const element = document.getElementById(id);
  if (element) element.innerText = text;
}

async function readErrorMessage(response, fallback) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map(item => item.msg).join("; ");
    return data.message || fallback;
  } catch {
    return fallback;
  }
}

function validateExamParams() {
  if (!maMH) return "Thieu ma mon hoc";
  if (!lanThi) return "Thieu lan thi";
  if (!maLop) return "Thieu ma lop";
  if (!ngayThi) return "Thieu ngay thi";
  return "";
}

async function loadStudentInfo() {
  const masv = window.currentUser?.ma;

  if (!masv) {
    setText("className", "Class: Khong tim thay thong tin dang nhap");
    return;
  }

  try {
    const res = await fetch(`/thi/nhanLop?masv=${encodeURIComponent(masv)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    if (res.ok) {
      const classInfo = await res.json();
      setText("className", `Class: ${classInfo.malop.trim()} - ${classInfo.tenlop}`);
      setText("studentName", `Student: ${masv}`);
    } else {
      setText("className", "Class: Khong tim thay lop");
    }
  } catch (error) {
    console.error("Loi:", error);
    setText("className", "Class: Loi ket noi may chu");
  }
}

async function loadQuestions() {
  const validationMessage = validateExamParams();
  if (validationMessage) {
    throw new Error(validationMessage);
  }

  const params = new URLSearchParams({
    mamonhoc: maMH,
    lanthi: lanThi,
    malop: maLop,
    ngaythi: ngayThi
  });

  const response = await fetch(`/thi/cau-hoi?${params.toString()}`);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Khong the tai cau hoi thi"));
  }

  const exam = await response.json();
  QUESTIONS = (exam.cauhoi || []).map((item, index) => ({
    id: item.cauhoi,
    number: index + 1,
    text: item.noidung,
    options: item.options || []
  }));
  timeLeft = (parseInt(exam.thoigian, 10) || 0) * 60;

  const examTitleEl = document.querySelector(".exam-header h2");
  if (examTitleEl) {
    examTitleEl.innerText = `Bai thi mon: ${exam.mamonhoc} (Lan ${exam.lanthi})`;
  }
}

function startTimer() {
  renderTimer();
  if (timerId) clearInterval(timerId);
  timerId = setInterval(() => {
    if (timeLeft > 0) timeLeft--;
    renderTimer();
  }, 1000);
}

function renderTimer() {
  const m = Math.floor(timeLeft / 60);
  const s = timeLeft % 60;
  setText("timer", String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0"));
}

function render() {
  if (!QUESTIONS.length) {
    setText("questionTitle", "Khong co cau hoi");
    setText("questionText", "Khong the tai danh sach cau hoi cho lich thi nay.");
    return;
  }

  const q = QUESTIONS[currentIdx];

  setText("questionTitle", `Question ${q.number}`);
  setText("questionText", q.text);

  const optionsDiv = document.getElementById("options");
  optionsDiv.innerHTML = "";

  q.options.forEach(opt => {
    const div = document.createElement("div");
    div.className = "option";
    div.innerText = `${opt.key}. ${opt.text}`;

    if (answers[q.id] === opt.key) {
      div.classList.add("active");
    }

    div.onclick = () => {
      answers[q.id] = opt.key;
      render();
    };

    optionsDiv.appendChild(div);
  });

  const grid = document.getElementById("navGrid");
  grid.innerHTML = "";

  QUESTIONS.forEach((question, idx) => {
    const btn = document.createElement("button");
    btn.innerText = question.number;

    if (idx === currentIdx) btn.style.background = "yellow";
    if (answers[question.id]) btn.style.background = "green";

    btn.onclick = () => {
      currentIdx = idx;
      render();
    };

    grid.appendChild(btn);
  });

  setText("progress", Object.keys(answers).length + "/" + QUESTIONS.length);
  setText("flagCount", flagged.size);
  document.getElementById("prevBtn").disabled = currentIdx === 0;
  document.getElementById("nextBtn").disabled = currentIdx === QUESTIONS.length - 1;
}

function nextQuestion() {
  if (currentIdx < QUESTIONS.length - 1) {
    currentIdx++;
    render();
  }
}

function prevQuestion() {
  if (currentIdx > 0) {
    currentIdx--;
    render();
  }
}

function toggleFlag() {
  const question = QUESTIONS[currentIdx];
  if (!question) return;

  if (flagged.has(question.id)) flagged.delete(question.id);
  else flagged.add(question.id);
  render();
}

function submitExam() {
  alert("Submitted!");
  console.log(answers);
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadStudentInfo();

  try {
    await loadQuestions();
    startTimer();
    render();
  } catch (error) {
    console.error("Loi tai cau hoi:", error);
    window.notify?.(error.message, "error");
    setText("questionTitle", "Khong the tai cau hoi");
    setText("questionText", error.message);
  }
});

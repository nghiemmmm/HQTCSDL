const urlParams = new URLSearchParams(window.location.search);
const maMH = urlParams.get("mamonhoc") || "";
const lanThi = urlParams.get("lanthi") || "";
const maLop = urlParams.get("malop") || "";
const ngayThi = urlParams.get("ngaythi") || "";

let QUESTIONS = [];
let currentIdx = 0;
let answers = {};
let timeLeft = 0;
let timerId = null;
let viewMode = "single";
let questionFontSize = 16;
let examSubmitted = false;
let examSessionId = null;
let autoSaveTimerId = null;

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
  const fullName = [window.currentUser?.ho, window.currentUser?.ten]
    .filter(Boolean)
    .join(" ")
    .trim();
  const displayName = fullName || masv;

  if (!masv) {
    setText("studentName", "Khong tim thay thong tin dang nhap");
    setText("className", "Lop: N/A");
    return;
  }

  try {
    const res = await fetch(`/thi/nhanLop?masv=${encodeURIComponent(masv)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    if (res.ok) {
      const classInfo = await res.json();
      setText("studentName", displayName);
      setText("className", `${classInfo.malop.trim()} - ${classInfo.tenlop}`);
    } else {
      setText("studentName", displayName);
      setText("className", "Khong tim thay lop");
    }
  } catch (error) {
    console.error("Loi:", error);
    setText("studentName", displayName);
    setText("className", "Loi ket noi may chu");
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
  examSessionId = exam.session_id || null;
  QUESTIONS = (exam.cauhoi || []).map((item, index) => ({
    id: item.cauhoi,
    number: index + 1,
    text: item.noidung,
    options: item.options || []
  }));
  answers = exam.answers || {};
  currentIdx = Math.min(Math.max(parseInt(exam.current_index, 10) || 0, 0), Math.max(QUESTIONS.length - 1, 0));
  timeLeft = parseInt(exam.remaining_seconds, 10);
  if (Number.isNaN(timeLeft)) {
    timeLeft = (parseInt(exam.thoigian, 10) || 0) * 60;
  }
  setText("examTitle", `Bai thi mon: ${exam.mamonhoc} (Lan ${exam.lanthi})`);
}

function startTimer() {
  renderTimer();
  if (timerId) clearInterval(timerId);
  timerId = setInterval(() => {
    if (timeLeft > 0) timeLeft--;
    if (timeLeft === 0 && !examSubmitted) {
      autoSaveExamState();
      window.notify?.("Da het thoi gian lam bai", "error");
    }
    renderTimer();
  }, 1000);
}

function renderTimer() {
  setText("timer", formatTime(timeLeft));
}

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return [h, m, s].map(value => String(value).padStart(2, "0")).join(":");
}

function getAnsweredCount() {
  return Object.keys(answers).length;
}

function updateSummary() {
  setText("progress", `${getAnsweredCount()}/${QUESTIONS.length}`);
  setText("answeredCount", getAnsweredCount());
  setText("totalCount", QUESTIONS.length);
}

function createOption(question, option) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "option";
  button.disabled = examSubmitted;
  if (answers[question.id] === option.key) {
    button.classList.add("active");
  }

  const key = document.createElement("span");
  key.className = "option-key";
  key.innerText = option.key;

  const text = document.createElement("span");
  text.innerText = option.text;

  button.append(key, text);
  button.addEventListener("click", () => {
    if (examSubmitted) return;
    answers[question.id] = option.key;
    autoSaveExamState();
    render();
  });

  return button;
}

function createQuestionCard(question, isCurrent) {
  const card = document.createElement("article");
  card.className = `question-card${isCurrent ? " is-current" : ""}`;
  card.id = `question-${question.number}`;

  const head = document.createElement("div");
  head.className = "question-card-head";

  const title = document.createElement("h2");
  title.innerText = `Cau ${question.number}`;

  const status = document.createElement("span");
  status.innerText = answers[question.id] ? "Da chon" : "Chua chon";

  head.append(title, status);

  const body = document.createElement("div");
  body.className = "question-card-body";

  const questionText = document.createElement("p");
  questionText.className = "question-text";
  questionText.innerText = question.text;

  const hint = document.createElement("p");
  hint.className = "answer-hint";
  hint.innerText = "Chọn một đáp án đúng";

  const options = document.createElement("div");
  options.className = "options";
  question.options.forEach(option => {
    options.appendChild(createOption(question, option));
  });

  body.append(questionText, hint, options);
  card.append(head, body);

  return card;
}

function renderQuestionHost() {
  const host = document.getElementById("questionHost");
  if (!host) return;

  host.innerHTML = "";

  if (!QUESTIONS.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerText = "Khong the tai danh sach cau hoi cho lich thi nay.";
    host.appendChild(empty);
    return;
  }

  if (viewMode === "all") {
    QUESTIONS.forEach((question, idx) => {
      host.appendChild(createQuestionCard(question, idx === currentIdx));
    });
    return;
  }

  host.appendChild(createQuestionCard(QUESTIONS[currentIdx], true));

  const pager = document.createElement("div");
  pager.className = "question-pager";

  const prev = document.createElement("button");
  prev.type = "button";
  prev.className = "exam-btn exam-btn-ghost";
  prev.innerText = "Cau truoc";
  prev.disabled = currentIdx === 0;
  prev.addEventListener("click", prevQuestion);

  const next = document.createElement("button");
  next.type = "button";
  next.className = "exam-btn exam-btn-ghost";
  next.innerText = "Cau tiep";
  next.disabled = currentIdx === QUESTIONS.length - 1;
  next.addEventListener("click", nextQuestion);

  pager.append(prev, next);
  host.appendChild(pager);
}

function renderNavigator() {
  const grid = document.getElementById("navGrid");
  if (!grid) return;

  grid.innerHTML = "";
  QUESTIONS.forEach((question, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.innerText = question.number;
    btn.disabled = examSubmitted;
    if (idx === currentIdx) btn.classList.add("is-current");
    if (answers[question.id]) btn.classList.add("is-answered");
    btn.addEventListener("click", () => {
      if (examSubmitted) return;
      currentIdx = idx;
      autoSaveExamState();
      render();
      if (viewMode === "all") {
        document.getElementById(`question-${question.number}`)?.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }
    });
    grid.appendChild(btn);
  });
}

function renderModeButton() {
  const button = document.getElementById("viewModeBtn");
  if (!button) return;
  button.innerText = viewMode === "single" ? "Danh sách câu hỏi" : "Từng câu";
}

function render() {
  renderModeButton();
  renderQuestionHost();
  renderNavigator();
  updateSummary();
}

function nextQuestion() {
  if (currentIdx < QUESTIONS.length - 1) {
    currentIdx++;
    autoSaveExamState();
    render();
  }
}

function prevQuestion() {
  if (currentIdx > 0) {
    currentIdx--;
    autoSaveExamState();
    render();
  }
}

function toggleViewMode() {
  viewMode = viewMode === "single" ? "all" : "single";
  render();
}

function changeFontSize(delta) {
  questionFontSize = Math.min(22, Math.max(14, questionFontSize + delta));
  document.querySelector(".exam-room")?.style.setProperty("--question-font-size", `${questionFontSize}px`);
}

function submitExam() {
  if (examSubmitted) return;
  openSubmitModal();
}

function openSubmitModal() {
  const modal = document.getElementById("submitModal");
  const unanswered = QUESTIONS.length - getAnsweredCount();
  const warning = document.getElementById("modalWarning");

  setText("modalTimeText", `Thời gian làm bài của bạn còn: ${formatTime(timeLeft)}`);

  if (warning) {
    warning.innerText = `Cảnh báo: Bạn còn ${unanswered} câu hỏi trắc nghiệm chưa trả lời. Bạn có chắc muốn kết thúc bài thi?`;
    warning.hidden = unanswered === 0;
  }
  if (modal) modal.hidden = false;
}

function closeSubmitModal() {
  const modal = document.getElementById("submitModal");
  if (modal) modal.hidden = true;
}

async function confirmSubmitExam() {
  await autoSaveExamState();
  const confirmButton = document.getElementById("confirmSubmitBtn");
  if (confirmButton) {
    confirmButton.disabled = true;
    confirmButton.innerText = "Dang nop...";
  }

  try {
    const response = await fetch("/thi/nop-bai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mamonhoc: maMH,
        session_id: examSessionId,
        lanthi: parseInt(lanThi, 10),
        malop: maLop,
        ngaythi: ngayThi,
        answers
      })
    });

    if (!response.ok) {
      throw new Error(await readErrorMessage(response, "Khong the nop bai thi"));
    }

    const result = await response.json();
    examSubmitted = true;
    document.querySelector(".exam-room")?.classList.add("is-submitted");
    document.getElementById("submitBtn")?.setAttribute("disabled", "disabled");
    if (timerId) clearInterval(timerId);
    if (autoSaveTimerId) clearInterval(autoSaveTimerId);
    closeSubmitModal();
    render();
    window.notify?.(`Da nop bai. Diem: ${result.diem}`, "success");
    if (result.practice) {
      return;
    }
    window.location.href = `/thi/xem-lai?session_id=${result.session_id || examSessionId}`;
  } catch (error) {
    window.notify?.(error.message, "error");
  } finally {
    if (confirmButton) {
      confirmButton.disabled = false;
      confirmButton.innerText = "Nộp bài";
    }
  }
}

async function autoSaveExamState() {
  if (!examSessionId || examSubmitted) return;

  try {
    const response = await fetch("/thi/autosave", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: examSessionId,
        answers,
        current_index: currentIdx,
        remaining_seconds: timeLeft
      })
    });

    if (response.ok) {
      const data = await response.json();
      if (typeof data.remaining_seconds === "number") {
        timeLeft = data.remaining_seconds;
        renderTimer();
      }
      if (data.status && data.status !== "DANG_LAM") {
        examSubmitted = true;
        document.querySelector(".exam-room")?.classList.add("is-submitted");
        document.getElementById("submitBtn")?.setAttribute("disabled", "disabled");
        if (timerId) clearInterval(timerId);
        if (autoSaveTimerId) clearInterval(autoSaveTimerId);
        render();
      }
    }
  } catch (error) {
    console.error("Autosave failed:", error);
  }
}

function bindControls() {
  document.getElementById("backBtn")?.addEventListener("click", () => {
    window.location.href = "/thi/";
  });
  document.getElementById("decreaseFontBtn")?.addEventListener("click", () => changeFontSize(-1));
  document.getElementById("increaseFontBtn")?.addEventListener("click", () => changeFontSize(1));
  document.getElementById("viewModeBtn")?.addEventListener("click", toggleViewMode);
  document.getElementById("submitBtn")?.addEventListener("click", submitExam);
  document.getElementById("cancelSubmitBtn")?.addEventListener("click", closeSubmitModal);
  document.getElementById("confirmSubmitBtn")?.addEventListener("click", confirmSubmitExam);
  document.getElementById("submitModal")?.addEventListener("click", (event) => {
    if (event.target.id === "submitModal") closeSubmitModal();
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  bindControls();
  await loadStudentInfo();

  try {
    await loadQuestions();
    startTimer();
    autoSaveTimerId = setInterval(autoSaveExamState, 10000);
    window.addEventListener("beforeunload", () => {
      if (!examSessionId || examSubmitted) return;
      const payload = JSON.stringify({
        session_id: examSessionId,
        answers,
        current_index: currentIdx,
        remaining_seconds: timeLeft
      });
      navigator.sendBeacon?.("/thi/autosave", new Blob([payload], { type: "application/json" }));
    });
    render();
  } catch (error) {
    console.error("Loi tai cau hoi:", error);
    window.notify?.(error.message, "error");
    setText("examTitle", "Khong the tai cau hoi");
    const host = document.getElementById("questionHost");
    if (host) {
      host.innerHTML = "";
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.innerText = error.message;
      host.appendChild(empty);
    }
  }
});

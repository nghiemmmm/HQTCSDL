document.addEventListener("DOMContentLoaded", async () => {
  const masv = "001"; // Mặc định ban đầu
  try {
    const res = await fetch(`/thi/nhanLop?masv=${masv}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (res.ok) {
      const classInfo = await res.json();
      document.getElementById("className").innerText = `Class: ${classInfo.malop.trim()} - ${classInfo.tenlop}`;
      document.getElementById("studentName").innerText = `Student: ${masv}`;
    } else {
      document.getElementById("className").innerText = "Class: Không tìm thấy lớp";
    }
  } catch (error) {
    console.error("Lỗi:", error);
    document.getElementById("className").innerText = "Class: Lỗi kết nối máy chủ";
  }
});

const QUESTIONS = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  text: "Question " + (i + 1),
  options: ["A", "B", "C", "D"]
}));

let currentIdx = 5;
let answers = {};
let flagged = new Set();
let timeLeft = 59 * 60 + 45;

/* TIMER */
setInterval(() => {
  if (timeLeft > 0) timeLeft--;
  renderTimer();
}, 1000);

function renderTimer() {
  const m = Math.floor(timeLeft / 60);
  const s = timeLeft % 60;
  document.getElementById("timer").innerText =
    String(m).padStart(2, '0') + ":" + String(s).padStart(2, '0');
}

/* RENDER */
function render() {
  const q = QUESTIONS[currentIdx];

  document.getElementById("questionTitle").innerText =
    `Question ${q.id}`;

  document.getElementById("questionText").innerText = q.text;

  const optionsDiv = document.getElementById("options");
  optionsDiv.innerHTML = "";

  q.options.forEach(opt => {
    const div = document.createElement("div");
    div.className = "option";
    div.innerText = opt;

    if (answers[currentIdx] === opt) {
      div.classList.add("active");
    }

    div.onclick = () => {
      answers[currentIdx] = opt;
      render();
    };

    optionsDiv.appendChild(div);
  });

  /* navigator */
  const grid = document.getElementById("navGrid");
  grid.innerHTML = "";

  QUESTIONS.forEach((q, idx) => {
    const btn = document.createElement("button");
    btn.innerText = q.id;

    if (idx === currentIdx) btn.style.background = "yellow";
    if (answers[idx]) btn.style.background = "green";

    btn.onclick = () => {
      currentIdx = idx;
      render();
    };

    grid.appendChild(btn);
  });

  document.getElementById("progress").innerText =
    Object.keys(answers).length + "/" + QUESTIONS.length;

  document.getElementById("flagCount").innerText = flagged.size;

  document.getElementById("prevBtn").disabled = currentIdx === 0;
  document.getElementById("nextBtn").disabled = currentIdx === QUESTIONS.length - 1;
}

/* ACTIONS */
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
  if (flagged.has(currentIdx)) flagged.delete(currentIdx);
  else flagged.add(currentIdx);
  render();
}

function submitExam() {
  alert("Submitted!");
  console.log(answers);
}

/* INIT */
render();
renderTimer();

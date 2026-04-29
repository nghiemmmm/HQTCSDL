document.addEventListener("DOMContentLoaded", () => {

  // 🔥 LẤY DATA TỪ BACKEND (KHÔNG FETCH)
  data = (initialMonHocs || []).map(item => ({
    maMH: ((item.mamh ?? item.maMH ?? "") + "").trim(),
    tenMH: ((item.tenmh ?? item.tenMH ?? "") + "").trim(),
  }));

  render();
  setState(`Đã tải ${data.length} môn học.`);

  // search
  maMHInput.addEventListener("input", () => {
    if (isSua) return;

    selectedIndex = -1;
    render();

    const prefix = maMHInput.value.trim();
    if (!prefix) return;

    const count = data.filter((item) =>
      (item.maMH || "").toUpperCase().startsWith(prefix.toUpperCase())
    ).length;

    setState(`Có ${count} môn học có mã bắt đầu bằng: ${prefix}`);
  });
});


// ====== BIẾN ======
let data = [];
let selectedIndex = -1;
let editingMamh = null;

let isThem = false;
let isSua = false;

let stackUndo = [];
let stackRedo = [];

const maMHInput = document.getElementById("maMH");
const tenMHInput = document.getElementById("tenMH");
const stateText = document.getElementById("stateText");


// ====== CORE ======
function setState(message) {
  stateText.textContent = message || "";
}

function render() {
  const tbody = document.getElementById("tbody");
  tbody.innerHTML = "";

  const prefix = maMHInput.value.trim().toUpperCase();

  data.forEach((item, index) => {
    if (prefix && !(item.maMH || "").toUpperCase().startsWith(prefix)) return;

    const row = document.createElement("tr");
    if (index === selectedIndex) row.classList.add("selected");

    row.innerHTML = `
      <td>${item.maMH}</td>
      <td>${item.tenMH}</td>
    `;

    row.onclick = () => selectRow(index);
    tbody.appendChild(row);
  });
}

function selectRow(index) {
  selectedIndex = index;
  maMHInput.value = data[index].maMH;
  tenMHInput.value = data[index].tenMH;
  setState("Đang chọn 1 môn học để thao tác.");
  render();
}
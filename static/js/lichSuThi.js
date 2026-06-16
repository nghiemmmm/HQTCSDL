function normalize(value) {
  return (value || "").toString().trim().toLowerCase();
}

function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function matchTimeFilter(value, filter) {
  if (!filter) return true;
  if (!value) return false;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return false;

  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const sevenDaysMs = 7 * 24 * 60 * 60 * 1000;

  if (filter === "today") return isSameDay(date, now);
  if (filter === "week") return Math.abs(diffMs) <= sevenDaysMs;
  if (filter === "past") return diffMs < 0;
  if (filter === "future") return diffMs >= 0;
  return true;
}

function applyHistoryFilters() {
  const keyword = normalize(document.getElementById("historySearch")?.value);
  const subject = normalize(document.getElementById("subjectFilter")?.value);
  const status = normalize(document.getElementById("statusFilter")?.value);
  const time = normalize(document.getElementById("timeFilter")?.value);

  document.querySelectorAll(".exam-list").forEach((list) => {
    let visibleCount = 0;
    const cards = list.querySelectorAll(".exam-history-card");

    list.querySelector(".history-empty")?.remove();

    cards.forEach((card) => {
      const matched = (!keyword || normalize(card.dataset.search).includes(keyword))
        && (!subject || normalize(card.dataset.subject) === subject)
        && (!status || normalize(card.dataset.status) === status)
        && matchTimeFilter(card.dataset.start, time);

      card.hidden = !matched;
      if (matched) visibleCount += 1;
    });

    const panel = list.closest(".history-panel");
    const badge = panel?.querySelector(".count-badge");
    if (badge) badge.innerText = visibleCount;

    if (!visibleCount) {
      const empty = document.createElement("div");
      empty.className = "history-empty";
      empty.innerText = list.dataset.emptyText || "Không có dữ liệu phù hợp";
      list.appendChild(empty);
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  ["historySearch", "subjectFilter", "statusFilter", "timeFilter"].forEach((id) => {
    document.getElementById(id)?.addEventListener("input", applyHistoryFilters);
    document.getElementById(id)?.addEventListener("change", applyHistoryFilters);
  });

  applyHistoryFilters();
});

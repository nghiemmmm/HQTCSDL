import re

# 1. Update formBoDe.html
with open('templates/formBoDe.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace input with select
old_input_regex = r'<input\s+id="searchBoDe"\s+type="search"\s+placeholder="\{% if user\.role.*?%\}">\s*'

new_select = """<select id="searchBoDe">
            <option value="">-- Tất cả môn học --</option>
            {% for mh in monhocs %}
            <option value="{{ mh.mamh }}">{{ mh.mamh }} - {{ mh.tenmh }}</option>
            {% endfor %}
          </select>\n          """

html = re.sub(old_input_regex, new_select, html, flags=re.DOTALL)
html = re.sub(r'boDe\.js\?v=\d+', 'boDe.js?v=14', html)

with open('templates/formBoDe.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update boDe.js
with open('static/js/boDe.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Update getFilteredRows
old_filter = """  function getFilteredRows() {
    const keyword = searchBoDeInput ? searchBoDeInput.value.trim().toLowerCase() : "";
    return data
      .map((item, index) => ({ item, index }))
      .filter(({ item }) => {
        if (!keyword) return true;
        const matchNoidung = (item.noidung || "").toLowerCase().includes(keyword);
        const matchMaMH = (item.mamh || "").toLowerCase().includes(keyword);
        const matchMaGV = (item.magv || "").toLowerCase().includes(keyword);
        return matchNoidung || matchMaMH || matchMaGV;
      });
  }"""

new_filter = """  function getFilteredRows() {
    const selectedMaMH = searchBoDeInput ? searchBoDeInput.value : "";
    return data
      .map((item, index) => ({ item, index }))
      .filter(({ item }) => {
        if (!selectedMaMH) return true;
        return (item.mamh || "").trim() === selectedMaMH;
      });
  }"""

js = js.replace(old_filter, new_filter)

# Change input event to change event
js = js.replace('searchBoDeInput.addEventListener("input", () => {', 'searchBoDeInput.addEventListener("change", () => {')

with open('static/js/boDe.js', 'w', encoding='utf-8') as f:
    f.write(js)

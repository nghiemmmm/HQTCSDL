import re

# 1. Update formBoDe.html
with open('templates/formBoDe.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_trinhdo_select = """        </select>
        <select id="searchTrinhDo" style="margin-left: 8px;">
          <option value="">-- Tất cả trình độ --</option>
          <option value="A">Trình độ A</option>
          <option value="B">Trình độ B</option>
          <option value="C">Trình độ C</option>
        </select>"""

if 'id="searchTrinhDo"' not in html:
    html = html.replace('</select>', new_trinhdo_select, 1) # Only replace the first </select> which is searchBoDe
    html = re.sub(r'boDe\.js\?v=\d+', 'boDe.js?v=15', html)
    with open('templates/formBoDe.html', 'w', encoding='utf-8') as f:
        f.write(html)

# 2. Update boDe.js
with open('static/js/boDe.js', 'r', encoding='utf-8') as f:
    js = f.read()

if 'searchTrinhDoInput' not in js:
    js = js.replace('const searchBoDeInput = document.getElementById("searchBoDe");', 
                    'const searchBoDeInput = document.getElementById("searchBoDe");\nconst searchTrinhDoInput = document.getElementById("searchTrinhDo");')

# Replace getFilteredRows completely
old_filter_regex = r'function getFilteredRows\(\)\s*\{.*?\}'
new_filter = """function getFilteredRows() {
  const selectedMaMH = searchBoDeInput ? searchBoDeInput.value.trim() : "";
  const selectedTrinhDo = searchTrinhDoInput ? searchTrinhDoInput.value.trim() : "";
  
  return data
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => {
      if (selectedMaMH && (item.mamh || "").trim() !== selectedMaMH) return false;
      if (selectedTrinhDo && (item.trinhdo || "").trim() !== selectedTrinhDo) return false;
      return true;
    });
}"""
js = re.sub(old_filter_regex, new_filter, js, flags=re.DOTALL)

# Add event listener for searchTrinhDoInput
old_listener = """  if (searchBoDeInput) {
    searchBoDeInput.addEventListener("change", () => {
      selectedIndex = -1;
      currentPage = 1;
      clearForm();
      disableAllInputs(true);
      render();
    });
  }"""

new_listener = """  const onFilterChange = () => {
    selectedIndex = -1;
    currentPage = 1;
    clearForm();
    disableAllInputs(true);
    render();
  };
  
  if (searchBoDeInput) {
    searchBoDeInput.addEventListener("change", onFilterChange);
  }
  if (searchTrinhDoInput) {
    searchTrinhDoInput.addEventListener("change", onFilterChange);
  }"""
js = js.replace(old_listener, new_listener)

# Fallback for old listener if the first replace failed (e.g. if it was "input")
old_listener_input = """  if (searchBoDeInput) {
    searchBoDeInput.addEventListener("input", () => {
      selectedIndex = -1;
      currentPage = 1;
      clearForm();
      disableAllInputs(true);
      render();
    });
  }"""
js = js.replace(old_listener_input, new_listener)

with open('static/js/boDe.js', 'w', encoding='utf-8') as f:
    f.write(js)

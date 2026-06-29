import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update window.undo
old_undo_start = """window.undo = async function() {
    clearError();
  if (isThem || isSua) return showError("KhA'ng th undo lAc nAy");"""

# It might have encoding issues, so let's use regex
pattern_undo = r'window\.undo\s*=\s*async\s*function\(\)\s*\{\s*clearError\(\);\s*if\s*\(isThem\s*\|\|\s*isSua\)\s*return\s*showError\([^)]+\);'

new_undo = """window.undo = async function() {
    clearError();
    if (isSua && selectedIndex >= 0) {
        var original = data[selectedIndex];
        if (tenMHInput) {
            tenMHInput.value = original.tenMH;
        }
        if (btnUndo) btnUndo.style.display = "none";
        return;
    }
    if (isThem) return showError("Không thể undo lúc này");"""

js = re.sub(pattern_undo, new_undo, js)

# 2. Add input listener for tenMHInput to show/hide undo button
listener_code = """
if (tenMHInput) {
    tenMHInput.addEventListener('input', function() {
        if (isSua && selectedIndex >= 0) {
            var original = data[selectedIndex];
            if (this.value.trim() !== (original.tenMH || "").trim()) {
                if (btnUndo) btnUndo.style.display = "inline-block";
            } else {
                if (btnUndo) btnUndo.style.display = "none";
            }
        }
    });
}
"""

js += listener_code

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=21', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

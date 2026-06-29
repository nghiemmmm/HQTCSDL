import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update setButtonState to always hide btnUndo by default
# It used to say:
# var showUndo = stackUndo.length > 0 ? "inline-block" : "none";
# and then uses `showUndo` in 'initial' and 'default' states.
js = js.replace('btnUndo.style.display = showUndo', 'btnUndo.style.display = "none"')

# 2. Clean up window.undo to ONLY revert the input field during edit
old_undo_regex = r'window\.undo\s*=\s*async\s*function\(\)\s*\{[\s\S]*?(?=\n\s*// Real-time validation)'

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
};"""

js = re.sub(old_undo_regex, new_undo, js)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=22', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

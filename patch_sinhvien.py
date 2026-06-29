import re

# 1. Update sinhVien_v28.js
with open('static/js/sinhVien_v28.js', 'r', encoding='utf-8') as f:
    js = f.read()

new_validation_logic = """
// ====== REALTIME VALIDATION ======
let svMaBlockedKeys = 0;
function preventInvalidMaSVChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) { svMaBlockedKeys = 0; return; }
    if (e.key === "Backspace") {
        if (svMaBlockedKeys > 0) { svMaBlockedKeys--; e.preventDefault(); return; }
        return;
    }
    if (e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "Delete") { svMaBlockedKeys = 0; return; }
    if (e.key.length === 1 && !/^[a-zA-Z0-9]$/.test(e.key)) {
        e.preventDefault(); svMaBlockedKeys++;
    } else if (e.key.length === 1) { svMaBlockedKeys = 0; }
}

function handleMaSVPaste(e) {
    e.preventDefault();
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    paste = paste.replace(/[^a-zA-Z0-9]/g, '');
    document.execCommand("insertText", false, paste);
}

function preventInvalidSVNameChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && /[0-9!@#$%^&*()_+\\-=\\[\\]{};':"\\\\|,.<>\\/?`~]/.test(e.key)) {
        e.preventDefault();
    }
}

function handleSVNamePaste(e) {
    e.preventDefault();
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    paste = paste.replace(/[0-9!@#$%^&*()_+\\-=\\[\\]{};':"\\\\|,.<>\\/?`~]/g, '');
    document.execCommand("insertText", false, paste);
}

function preventInvalidClassNameChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && /[!@#$%^&*()_+\\-=\\[\\]{};':"\\\\|,.<>\\/?`~]/.test(e.key)) {
        e.preventDefault();
    }
}

function handleClassNamePaste(e) {
    e.preventDefault();
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    paste = paste.replace(/[!@#$%^&*()_+\\-=\\[\\]{};':"\\\\|,.<>\\/?`~]/g, '');
    document.execCommand("insertText", false, paste);
}

// Bind events if elements exist
if (typeof txtMaSV !== 'undefined' && txtMaSV) {
    txtMaSV.addEventListener("keydown", preventInvalidMaSVChars);
    txtMaSV.addEventListener("paste", handleMaSVPaste);
    txtMaSV.addEventListener("mousedown", () => svMaBlockedKeys = 0);
    txtMaSV.addEventListener("blur", () => svMaBlockedKeys = 0);
}
if (typeof txtMaLop !== 'undefined' && txtMaLop) {
    txtMaLop.addEventListener("keydown", preventInvalidMaSVChars);
    txtMaLop.addEventListener("paste", handleMaSVPaste);
    txtMaLop.addEventListener("mousedown", () => svMaBlockedKeys = 0);
    txtMaLop.addEventListener("blur", () => svMaBlockedKeys = 0);
}
if (typeof txtHoTen !== 'undefined' && txtHoTen) {
    txtHoTen.addEventListener("keydown", preventInvalidSVNameChars);
    txtHoTen.addEventListener("paste", handleSVNamePaste);
}
if (typeof txtTenLop !== 'undefined' && txtTenLop) {
    txtTenLop.addEventListener("keydown", preventInvalidClassNameChars);
    txtTenLop.addEventListener("paste", handleClassNamePaste);
}
"""

js += new_validation_logic

with open('static/js/sinhVien_v28.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formSinhVien.html to bump JS version
with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'sinhVien_v28\.js\?v=\d+', 'sinhVien_v28.js?v=8', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

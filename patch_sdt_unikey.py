import re

# 1. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_code = """function preventInvalidPhoneChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && !/^[0-9]$/.test(e.key)) {
        e.preventDefault();
    }
}

function handlePhonePaste(e) {
    e.preventDefault();
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    paste = paste.replace(/[^0-9]/g, '');
    document.execCommand("insertText", false, paste);
}

if (sdtGVInput) {
    sdtGVInput.addEventListener("keydown", preventInvalidPhoneChars);
    sdtGVInput.addEventListener("paste", handlePhonePaste);
}"""

new_code = """let phoneBlockedKeys = 0;

function preventInvalidPhoneChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) {
        phoneBlockedKeys = 0;
        return;
    }
    
    if (e.key === "Backspace") {
        if (phoneBlockedKeys > 0) {
            phoneBlockedKeys--;
            e.preventDefault();
            return;
        }
        return;
    }
    
    if (e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "Delete") {
        phoneBlockedKeys = 0;
        return;
    }
    
    if (e.key.length === 1 && !/^[0-9]$/.test(e.key)) {
        e.preventDefault();
        phoneBlockedKeys++;
    } else if (e.key.length === 1) {
        phoneBlockedKeys = 0;
    }
}

function handlePhonePaste(e) {
    e.preventDefault();
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    paste = paste.replace(/[^0-9]/g, '');
    document.execCommand("insertText", false, paste);
}

if (sdtGVInput) {
    sdtGVInput.addEventListener("keydown", preventInvalidPhoneChars);
    sdtGVInput.addEventListener("paste", handlePhonePaste);
    sdtGVInput.addEventListener("mousedown", () => phoneBlockedKeys = 0);
    sdtGVInput.addEventListener("blur", () => phoneBlockedKeys = 0);
}"""

js = js.replace(old_code, new_code)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formGiaoVien.html to bump JS version
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=20', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

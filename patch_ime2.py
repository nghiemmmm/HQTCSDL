import re

# 1. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_code = """if (hoGVInput) {
    hoGVInput.addEventListener("input", function() {
        let newVal = this.value.replace(/[^\\p{L}\\s]/gu, '');
        if (this.value !== newVal) {
            let start = this.selectionStart;
            let end = this.selectionEnd;
            this.value = newVal;
            this.setSelectionRange(start - 1, end - 1);
        }
    });
}
if (tenGVInput) {
    tenGVInput.addEventListener("input", function() {
        let newVal = this.value.replace(/[^\\p{L}\\s]/gu, '');
        if (this.value !== newVal) {
            let start = this.selectionStart;
            let end = this.selectionEnd;
            this.value = newVal;
            this.setSelectionRange(start - 1, end - 1);
        }
    });
}"""

new_code = """function preventInvalidNameChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key.length === 1 && /[0-9!@#$%^&*()_+\\-=\\[\\]{};':"\\\\|,.<>\\/?`~]/.test(e.key)) {
        e.preventDefault();
    }
}

function handleNamePaste(e) {
    e.preventDefault();
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    paste = paste.replace(/[0-9!@#$%^&*()_+\\-=\\[\\]{};':"\\\\|,.<>\\/?`~]/g, '');
    document.execCommand("insertText", false, paste);
}

if (hoGVInput) {
    hoGVInput.addEventListener("keydown", preventInvalidNameChars);
    hoGVInput.addEventListener("paste", handleNamePaste);
}
if (tenGVInput) {
    tenGVInput.addEventListener("keydown", preventInvalidNameChars);
    tenGVInput.addEventListener("paste", handleNamePaste);
}"""

js = js.replace(old_code, new_code)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formGiaoVien.html to bump JS version
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=18', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

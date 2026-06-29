import re

# 1. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

new_code = """let maBlockedKeys = 0;
function preventInvalidMaChars(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) {
        maBlockedKeys = 0;
        return;
    }
    
    if (e.key === "Backspace") {
        if (maBlockedKeys > 0) {
            maBlockedKeys--;
            e.preventDefault();
            return;
        }
        return;
    }
    
    if (e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "Delete") {
        maBlockedKeys = 0;
        return;
    }
    
    // Only allow alphanumeric characters (no spaces, no special chars, no accents)
    if (e.key.length === 1 && !/^[a-zA-Z0-9]$/.test(e.key)) {
        e.preventDefault();
        maBlockedKeys++;
    } else if (e.key.length === 1) {
        maBlockedKeys = 0;
    }
}

function handleMaPaste(e) {
    e.preventDefault();
    let paste = (e.clipboardData || window.clipboardData).getData('text');
    paste = paste.replace(/[^a-zA-Z0-9]/g, '');
    document.execCommand("insertText", false, paste);
}

if (maGVInput) {
    maGVInput.addEventListener("keydown", preventInvalidMaChars);
    maGVInput.addEventListener("paste", handleMaPaste);
    maGVInput.addEventListener("mousedown", () => maBlockedKeys = 0);
    maGVInput.addEventListener("blur", () => maBlockedKeys = 0);
}

let phoneBlockedKeys = 0;"""

js = js.replace('let phoneBlockedKeys = 0;', new_code)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formGiaoVien.html to bump JS version
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=21', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

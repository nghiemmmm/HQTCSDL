import re

# 1. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the problematic realtime name validation
old_validation = """if (hoGVInput) {
    hoGVInput.addEventListener("input", function() {
        this.value = this.value.replace(/[^\\p{L}\\s]/gu, '');
    });
}
if (tenGVInput) {
    tenGVInput.addEventListener("input", function() {
        this.value = this.value.replace(/[^\\p{L}\\s]/gu, '');
    });
}"""

new_validation = """if (hoGVInput) {
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

js = js.replace(old_validation, new_validation)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

# 2. Update formGiaoVien.html to bump JS version
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=17', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

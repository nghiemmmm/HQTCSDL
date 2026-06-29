import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Pattern to find and remove tenMHInput.focus() from window.them
# Only remove the one inside window.them (or we can just remove all of them if they are redundant, but better to be safe)
# The block is:
#     if(tenMHInput) {
#         tenMHInput.disabled = false;
#         tenMHInput.value = "";
#         tenMHInput.focus();
#     }
old_block = """    if(tenMHInput) {
        tenMHInput.disabled = false;
        tenMHInput.value = "";
        tenMHInput.focus();
    }"""
new_block = """    if(tenMHInput) {
        tenMHInput.disabled = false;
        tenMHInput.value = "";
    }"""

js = js.replace(old_block, new_block)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=17', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

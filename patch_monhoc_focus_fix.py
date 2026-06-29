import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Remove tenMHInput.focus() completely
js = re.sub(r'tenMHInput\.focus\(\);', '', js)

# 2. Make maMHInput.focus() reliable by using setTimeout
# Currently it is: maMHInput.focus();
# We replace it with: setTimeout(() => { maMHInput.focus(); }, 50);
js = re.sub(r'maMHInput\.focus\(\);', 'setTimeout(() => { maMHInput.focus(); }, 50);', js)

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=18', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('static/js/giaoVien_v2.js', 'r', encoding='utf-8') as f:
    c = f.read()

import re
c = re.sub(r'if \(searchGVInput\) \{\s*searchGVInput\.addEventListener\("input", \(\) => \{\s*if \(searchGVInput\) \{\s*searchGVInput\.addEventListener\("input", \(\) => \{', 
           r'if (searchGVInput) {\n    searchGVInput.addEventListener("input", () => {', c)

with open('static/js/giaoVien_v2.js', 'w', encoding='utf-8') as f:
    f.write(c)

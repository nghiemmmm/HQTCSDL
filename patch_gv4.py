import re

with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Hide formGrid at the end of ghi()
old_ghi_end = r'selectedIndex = -1;\n\s*setButtonState\("default"\);\n\n\s*render\(\);\n\s*\}'
new_ghi_end = """selectedIndex = -1;
    setButtonState("default");
    
    const fg = document.getElementById("formGrid");
    if (fg) fg.style.display = "none";

    render();
  }"""
js = re.sub(old_ghi_end, new_ghi_end, js)

# 2. Remove stackUndo.push for UPDATE in ghi()
old_push_update = r'stackUndo\.push\(\{ type: "UPDATE", old, new: result, index: selectedIndex \}\);'
js = re.sub(old_push_update, '// stackUndo.push({ type: "UPDATE", old, new: result, index: selectedIndex });', js)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=12', html)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

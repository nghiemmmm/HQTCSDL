import re

# 1. Update formGiaoVien.html
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Change btnThem to be larger, colorful, and right-aligned
old_them = r'<button id="btnThem"[^>]*>Them</button>'
new_them = '<button id="btnThem" onclick="them()" data-permission="create_teacher" style="margin-left: auto; padding: 10px 24px; font-size: 15px; font-weight: bold; background: linear-gradient(120deg, #0f8b8d, #1a6fba); color: white; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(15, 139, 141, 0.2);">Them</button>'
html = re.sub(old_them, new_them, html)

# Bump version
html = re.sub(r'giaoVien_v8\.js\?v=\d+', 'giaoVien_v8.js?v=11', html)

with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update giaoVien_v8.js
with open('static/js/giaoVien_v8.js', 'r', encoding='utf-8') as f:
    js = f.read()

# In setButtonState, for "selected", hide btnThem
js = js.replace('} else if (state === "selected") {\n    if (btnThem) btnThem.style.display = "inline-block";',
                '} else if (state === "selected") {\n    if (btnThem) btnThem.style.display = "none";')

# In selectRow, replace disabled = true with custom data attribute
old_select_disable = r'if \(btnSua\) \{ btnSua\.disabled = true; btnSua\.style\.opacity = 0\.5; btnSua\.title = "Giáo viên đã mở lớp thi, không thể sửa"; \}\s*if \(btnXoa\) \{ btnXoa\.disabled = true; btnXoa\.style\.opacity = 0\.5; btnXoa\.title = "Giáo viên đã mở lớp thi, không thể xóa"; \}'
new_select_disable = 'if (btnSua) { btnSua.disabled = false; btnSua.setAttribute("data-disabled", "true"); btnSua.style.opacity = 0.5; btnSua.style.cursor = "not-allowed"; }\n      if (btnXoa) { btnXoa.disabled = false; btnXoa.setAttribute("data-disabled", "true"); btnXoa.style.opacity = 0.5; btnXoa.style.cursor = "not-allowed"; }'
js = re.sub(old_select_disable, new_select_disable, js)

old_select_enable = r'if \(btnSua\) \{ btnSua\.disabled = false; btnSua\.style\.opacity = 1; btnSua\.title = ""; \}\s*if \(btnXoa\) \{ btnXoa\.disabled = false; btnXoa\.style\.opacity = 1; btnXoa\.title = ""; \}'
new_select_enable = 'if (btnSua) { btnSua.disabled = false; btnSua.removeAttribute("data-disabled"); btnSua.style.opacity = 1; btnSua.style.cursor = "pointer"; btnSua.title = ""; }\n  if (btnXoa) { btnXoa.disabled = false; btnXoa.removeAttribute("data-disabled"); btnXoa.style.opacity = 1; btnXoa.style.cursor = "pointer"; btnXoa.title = ""; }'
js = re.sub(old_select_enable, new_select_enable, js)


# In sua(), check data-disabled
old_sua = r'function sua\(\) \{\n\s*const fg = document\.getElementById\("formGrid"\);\n\s*if \(fg\) fg\.style\.display = "grid";\n\s*clearError\(\);'
new_sua = """function sua() {
    if (btnSua && btnSua.getAttribute("data-disabled") === "true") {
        showError("Giáo viên đã mở lớp thi hoặc có câu hỏi, không thể sửa!");
        return;
    }
    const fg = document.getElementById("formGrid");
    if (fg) fg.style.display = "grid";
    clearError();"""
js = re.sub(old_sua, new_sua, js)

# In xoa(), check data-disabled
old_xoa = r'function xoa\(\) \{\n\s*clearError\(\);'
new_xoa = """function xoa() {
    if (btnXoa && btnXoa.getAttribute("data-disabled") === "true") {
        showError("Giáo viên đã mở lớp thi hoặc có câu hỏi, không thể xóa!");
        return;
    }
    clearError();"""
js = re.sub(old_xoa, new_xoa, js)

with open('static/js/giaoVien_v8.js', 'w', encoding='utf-8') as f:
    f.write(js)

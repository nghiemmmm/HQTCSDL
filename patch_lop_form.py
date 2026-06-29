import re

# 1. Update formSinhVien.html
with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the old formLop section entirely
html = re.sub(r'\{% if is_class_page %\}.*?<section class="card form-card" id="formLop".*?</section>.*?\{% endif %\}', '', html, flags=re.DOTALL)

# Insert the new formLop inside grid-layout
new_formLop = """
    {% if is_class_page %}
    <section class="card form-card" id="formLop">
        <h3>Nhap thong tin lop</h3>
        <label for="txtMaLop">Ma lop</label>
        <input type="text" id="txtMaLop" maxlength="15" placeholder="VD: DA22TT01">

        <label for="txtTenLop">Ten lop</label>
        <input type="text" id="txtTenLop" placeholder="VD: Lop A">

        <div style="display: flex; gap: 10px; margin-top: 15px;">
            <button id="btnLopSave" type="button" data-any-permission="create_class,update_class">Luu lop</button>
            <button id="btnLopCancel" type="button">Huy</button>
            <button id="btnLopUndo" type="button" style="display: none; background: #6b7280; border: none; color: white; padding: 10px 16px; border-radius: var(--radius-md); cursor: pointer;" title="Khoi phuc ten lop goc">Undo</button>
        </div>
        <div id="errorLop" style="color: #dc2626; font-weight: 500; font-size: 14px; margin-top: 10px; min-height: 20px;"></div>
    </section>
    {% endif %}
"""
html = html.replace('<section class="grid-layout">', '<section class="grid-layout">' + new_formLop)

# Bump versions
html = re.sub(r'sinhVien\.css\?v=\d+', 'sinhVien.css?v=13', html)
html = re.sub(r'sinhVien_v28\.js\?v=3', 'sinhVien_v28.js?v=4', html) # Wait, it was v28.js?v=3

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 2. Update sinhVien.css
with open('static/css/sinhVien.css', 'r', encoding='utf-8') as f:
    css = f.read()

new_css = """
    .page-wrap[data-page-mode="class"] .grid-layout {
        grid-template-columns: 320px 1fr;
        align-items: start;
    }
"""
if '.page-wrap[data-page-mode="class"] .grid-layout' not in css:
    css = css.replace('@media (min-width: 960px) {', '@media (min-width: 960px) {\n' + new_css)

with open('static/css/sinhVien.css', 'w', encoding='utf-8') as f:
    f.write(css)


# 3. Update sinhVien_v28.js
with open('static/js/sinhVien_v28.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add btnLopUndo
js = js.replace('const btnLopCancel = document.getElementById("btnLopCancel");', 'const btnLopCancel = document.getElementById("btnLopCancel");\nconst btnLopUndo = document.getElementById("btnLopUndo");')

# Update showLopForm
old_showLopForm = r'function showLopForm\(showClassDetail = false\) \{[\s\S]*?\}'
new_showLopForm = """function showLopForm(showClassDetail = false) {
    if (formLop) formLop.style.display = "block";
}"""
js = re.sub(old_showLopForm, new_showLopForm, js)

# Update checkDuplicateLop to clear undo
js = js.replace('if (btnLopSave) btnLopSave.disabled = false;', 'if (btnLopSave) btnLopSave.disabled = false;\n            if (btnLopUndo) btnLopUndo.style.display = "none";')

# Hide undo on cancel
js = js.replace('clearLopForm();', 'clearLopForm();\n        if (btnLopUndo) btnLopUndo.style.display = "none";')

# Add undo logic block at the end of the file
undo_logic = """
if (txtTenLop) {
    txtTenLop.addEventListener('input', function() {
        if (currentFormAction === "edit_lop" && editingMaLop) {
            if (this.value.trim() !== (selectedLopTen || "").trim()) {
                if (btnLopUndo) btnLopUndo.style.display = "inline-block";
            } else {
                if (btnLopUndo) btnLopUndo.style.display = "none";
            }
        }
    });
}
if (btnLopUndo) {
    btnLopUndo.onclick = () => {
        if (currentFormAction === "edit_lop") {
            if (txtTenLop) txtTenLop.value = selectedLopTen;
            btnLopUndo.style.display = "none";
        }
    };
}
"""
js += undo_logic

with open('static/js/sinhVien_v28.js', 'w', encoding='utf-8') as f:
    f.write(js)


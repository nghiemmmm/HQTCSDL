import re

# 1. Update formSinhVien.html
with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the formLop section with a horizontally stretched version
old_form = r'<section class="card form-card" id="formLop">[\s\S]*?</section>'
new_form = """<section class="card form-card class-form-card" id="formLop" style="width: 100%;">
        <h3 style="margin-bottom: 15px;">Nhap thong tin lop</h3>
        <div style="display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px;">
                <label for="txtMaLop" style="display: block; margin-bottom: 5px;">Ma lop</label>
                <input type="text" id="txtMaLop" maxlength="15" placeholder="VD: DA22TT01">
            </div>
            <div style="flex: 2; min-width: 250px;">
                <label for="txtTenLop" style="display: block; margin-bottom: 5px;">Ten lop</label>
                <input type="text" id="txtTenLop" placeholder="VD: Lop A">
            </div>
            <div style="display: flex; gap: 10px; margin-top: 28px;">
                <button id="btnLopSave" type="button" data-any-permission="create_class,update_class">Luu lop</button>
                <button id="btnLopCancel" type="button">Huy</button>
                <button id="btnLopUndo" type="button" style="display: none; background: #6b7280; border: none; color: white; padding: 10px 16px; border-radius: var(--radius-md); cursor: pointer;" title="Khoi phuc ten lop goc">Undo</button>
            </div>
        </div>
        <div id="errorLop" style="color: #dc2626; font-weight: 500; font-size: 14px; margin-top: 10px; min-height: 20px;"></div>
    </section>"""
html = re.sub(old_form, new_form, html)

html = re.sub(r'sinhVien\.css\?v=\d+', 'sinhVien.css?v=14', html)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 2. Update sinhVien.css
with open('static/css/sinhVien.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace the 320px 1fr grid with minmax(0, 1fr)
css = css.replace('grid-template-columns: 320px 1fr;', 'grid-template-columns: minmax(0, 1fr);')

with open('static/css/sinhVien.css', 'w', encoding='utf-8') as f:
    f.write(css)

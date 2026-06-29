import re

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_block = """            <div class="card-head">
                <h3>Danh sach lop</h3>
                {% if is_class_page %}
                <button id="btnClassAdd" class="table-primary-action" type="button" data-permission="create_class">Them lop</button>
                {% else %}
                <span class="chip">Lop hoc</span>
                {% endif %}
            </div>
            <div class="class-filter" role="search">
                <input id="classFilterInput" type="search" placeholder="Tim theo ma lop hoac ten lop" aria-label="Tim theo ma lop hoac ten lop">
                <button id="classFilterClear" type="button">Xoa loc</button>
            </div>"""

new_block = """            <div class="class-filter" role="search" style="display: flex; gap: 10px; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <div style="display: flex; gap: 10px; align-items: center; flex: 1;">
                    <input id="classFilterInput" type="search" placeholder="Tim theo ma lop hoac ten lop" aria-label="Tim theo ma lop hoac ten lop" style="max-width: 350px;">
                    <button id="classFilterClear" type="button">Xoa loc</button>
                </div>
                
                {% if is_class_page %}
                <button id="btnClassAdd" class="table-primary-action" type="button" data-permission="create_class">Them lop</button>
                {% else %}
                <span class="chip">Lop hoc</span>
                {% endif %}
            </div>"""

html = html.replace(old_block, new_block)

# Bump CSS version just in case
html = re.sub(r'sinhVien\.css\?v=\d+', 'sinhVien.css?v=11', html)

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched formSinhVien.html layout successfully.")

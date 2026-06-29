import re

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Move btnBackToClasses
old_card_head = """
            <div class="card-head">
                <div>
                    <h3>Danh sach sinh vien</h3>
                    <p id="studentClassInfo" class="selection-note">Chua chon lop</p>
                </div>
                <span class="chip">Sinh vien</span>
            </div>
"""
new_card_head = """
            <div class="card-head">
                <div>
                    <h3>Danh sach sinh vien</h3>
                    <p id="studentClassInfo" class="selection-note">Chua chon lop</p>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button id="btnBackToClasses" type="button" style="background-color: #64748b; color: white; padding: 6px 12px; border-radius: 6px; font-size: 13px;">Chon lop khac</button>
                    <span class="chip">Sinh vien</span>
                </div>
            </div>
"""
html = html.replace(old_card_head.strip(), new_card_head.strip())

# Remove original btnBackToClasses
html = html.replace('<button id="btnBackToClasses" type="button">Chon lop khac</button>', '')

# Move Save and Cancel buttons
old_form_head = "<h3>Nhap thong tin sinh vien</h3>"
new_form_head = """
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0;">Nhap thong tin sinh vien</h3>
                    <div style="display: flex; gap: 10px;">
                        <button id="btnDetailSaveForm" type="button" style="padding: 6px 12px;">Luu sinh vien</button>
                        <button id="btnDetailCancel" type="button" style="padding: 6px 12px; background-color: #9ca3af; color: white;">Huy</button>
                    </div>
                </div>
"""
html = html.replace(old_form_head, new_form_head.strip())

# Remove original Save and Cancel buttons container
old_buttons_container = """
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button id="btnDetailSaveForm" type="button">Luu sinh vien</button>
                    <button id="btnDetailCancel" type="button">Huy</button>
                </div>
"""
html = html.replace(old_buttons_container.strip(), '')

# Remove extra empty div if any left, but we just replaced the exact string.

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully moved buttons.")

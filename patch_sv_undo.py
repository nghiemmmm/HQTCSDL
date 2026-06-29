import re

# 1. Update formSinhVien.html
with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add btnSVUndo next to btnDetailCancel
old_buttons = r'<div style="display: flex; gap: 10px;" id="formSinhVienButtons">.*?<button id="btnDetailCancel".*?</button>.*?</div>'
new_buttons = """<div style="display: flex; gap: 10px;" id="formSinhVienButtons">
                        <button id="btnDetailSaveForm" type="button" style="padding: 6px 12px;">Luu sinh vien</button>
                        <button id="btnDetailCancel" type="button" style="padding: 6px 12px; background-color: #9ca3af; color: white;">Huy</button>
                        <button id="btnSVUndo" type="button" style="display: none; padding: 6px 12px; background-color: #6b7280; color: white; border: none; border-radius: var(--radius-md); cursor: pointer;" title="Khoi phuc thong tin goc">Undo</button>
                    </div>"""
html = re.sub(old_buttons, new_buttons, html, flags=re.DOTALL)

html = re.sub(r'sinhVien_v28\.js\?v=\d+', 'sinhVien_v28.js?v=6', html)

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update sinhVien_v28.js
with open('static/js/sinhVien_v28.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Define btnSVUndo
js = js.replace('const btnDetailCancel = document.getElementById("btnDetailCancel");', 'const btnDetailCancel = document.getElementById("btnDetailCancel");\nconst btnSVUndo = document.getElementById("btnSVUndo");')

# Hide undo on clearStudentForm
js = js.replace('function clearStudentForm() {', 'function clearStudentForm() {\n    if (btnSVUndo) btnSVUndo.style.display = "none";')

# Hide undo on btnDetailCancel click
# btnDetailCancel is handled somewhere. Let's just append the logic at the end of the file.

undo_logic = """
function checkSVUndo() {
    if (currentFormAction === "edit_sv" && selectedStudentIndex >= 0 && dsSV[selectedStudentIndex]) {
        const student = dsSV[selectedStudentIndex];
        const isHoTenChanged = (txtHoTen && txtHoTen.value.trim() !== (student.hoTen || "").trim());
        const isNgaySinhChanged = (txtNgaySinh && txtNgaySinh.value !== normalizeDateValue(student.ngaySinh));
        
        if (isHoTenChanged || isNgaySinhChanged) {
            if (btnSVUndo) btnSVUndo.style.display = "inline-block";
        } else {
            if (btnSVUndo) btnSVUndo.style.display = "none";
        }
    } else {
        if (btnSVUndo) btnSVUndo.style.display = "none";
    }
}

if (txtHoTen) txtHoTen.addEventListener('input', checkSVUndo);
if (txtNgaySinh) {
    txtNgaySinh.addEventListener('input', checkSVUndo);
    txtNgaySinh.addEventListener('change', checkSVUndo);
}

if (btnSVUndo) {
    btnSVUndo.onclick = () => {
        if (currentFormAction === "edit_sv" && selectedStudentIndex >= 0 && dsSV[selectedStudentIndex]) {
            const student = dsSV[selectedStudentIndex];
            if (txtHoTen) txtHoTen.value = student.hoTen;
            if (txtNgaySinh) txtNgaySinh.value = normalizeDateValue(student.ngaySinh);
            btnSVUndo.style.display = "none";
            const errorSV = document.getElementById("errorSV");
            if (errorSV) errorSV.innerText = "";
            if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;
        }
    };
}
"""

js += undo_logic

with open('static/js/sinhVien_v28.js', 'w', encoding='utf-8') as f:
    f.write(js)

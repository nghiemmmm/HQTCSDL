import re
import os

html_path = 'templates/formSinhVien.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Inject errorLop
html = html.replace(
    '<button id="btnLopCancel" type="button">Huy</button>\n        </div>',
    '<button id="btnLopCancel" type="button">Huy</button>\n        </div>\n        <div id="errorLop" style="color: #dc2626; font-weight: 500; font-size: 14px; margin-top: 10px; min-height: 20px;"></div>'
)

# Inject errorSV
html = html.replace(
    '<button id="btnDetailCancel" type="button">Huy</button>\n                </div>',
    '<button id="btnDetailCancel" type="button">Huy</button>\n                </div>\n                <div id="errorSV" style="color: #dc2626; font-weight: 500; font-size: 14px; margin-top: 10px; min-height: 20px;"></div>'
)

# Bump version
html = re.sub(r'sinhVien\.js\?v=[\w\-]+', 'sinhVien_v2.js', html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)


js_path = 'static/js/sinhVien.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Update clearLopForm
js = js.replace(
'''function clearLopForm() {

    if (txtMaLop) {

        txtMaLop.value = "";

        txtMaLop.disabled = false;

    }

    if (txtTenLop) txtTenLop.value = "";

    if (viewClassMa) viewClassMa.textContent = "Chua chon";

    if (viewClassTen) viewClassTen.textContent = "Chua chon";

    if (classDetailPanel) classDetailPanel.style.display = "none";

}''',
'''function clearLopForm() {
    if (txtMaLop) {
        txtMaLop.value = "";
        txtMaLop.disabled = false;
    }
    if (txtTenLop) {
        txtTenLop.value = "";
        txtTenLop.disabled = false;
        txtTenLop.style.backgroundColor = "";
    }
    const errorLop = document.getElementById("errorLop");
    if (errorLop) errorLop.innerText = "";
    if (btnLopSave) btnLopSave.disabled = false;

    if (viewClassMa) viewClassMa.textContent = "Chua chon";
    if (viewClassTen) viewClassTen.textContent = "Chua chon";
    if (classDetailPanel) classDetailPanel.style.display = "none";
}'''
)

# Update clearStudentForm
js = js.replace(
'''function clearStudentForm() {

    if (txtMaSV) {

        txtMaSV.value = "";

        txtMaSV.disabled = false;

    }

    if (txtHoTen) txtHoTen.value = "";

    if (txtNgaySinh) txtNgaySinh.value = "";

    renderSelectedStudentInfo(null);

}''',
'''function clearStudentForm() {
    if (txtMaSV) {
        txtMaSV.value = "";
        txtMaSV.disabled = false;
    }
    if (txtHoTen) {
        txtHoTen.value = "";
        txtHoTen.disabled = false;
        txtHoTen.style.backgroundColor = "";
    }
    if (txtNgaySinh) {
        txtNgaySinh.value = "";
        txtNgaySinh.disabled = false;
        txtNgaySinh.style.backgroundColor = "";
    }
    const errorSV = document.getElementById("errorSV");
    if (errorSV) errorSV.innerText = "";
    if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;

    renderSelectedStudentInfo(null);
}'''
)

# edit class enable
js = js.replace(
'''        if (txtTenLop) txtTenLop.value = selectedLopTen;''',
'''        if (txtTenLop) { txtTenLop.value = selectedLopTen; txtTenLop.disabled = false; txtTenLop.style.backgroundColor = ""; }
        const errorLop = document.getElementById("errorLop");
        if (errorLop) errorLop.innerText = "";
        if (btnLopSave) btnLopSave.disabled = false;'''
)

# edit sv enable
js = js.replace(
'''        if (txtHoTen) txtHoTen.value = student.hoTen;

        if (txtNgaySinh) txtNgaySinh.value = normalizeDateValue(student.ngaySinh);''',
'''        if (txtHoTen) { txtHoTen.value = student.hoTen; txtHoTen.disabled = false; txtHoTen.style.backgroundColor = ""; }
        if (txtNgaySinh) { txtNgaySinh.value = normalizeDateValue(student.ngaySinh); txtNgaySinh.disabled = false; txtNgaySinh.style.backgroundColor = ""; }
        const errorSV = document.getElementById("errorSV");
        if (errorSV) errorSV.innerText = "";
        if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;'''
)


append_js = '''
function checkDuplicateLop() {
    if (currentFormAction === "add_lop") {
        const val = txtMaLop.value.trim();
        const errorLop = document.getElementById("errorLop");
        if (val) {
            const exists = dsLop.some(item => (item.maLop || "").trim().toLowerCase() === val.toLowerCase());
            if (exists) {
                if (errorLop) errorLop.innerText = `Mã lớp ${val} đã tồn tại`;
                if (btnLopSave) btnLopSave.disabled = true;
                if (txtTenLop) {
                    txtTenLop.disabled = true;
                    txtTenLop.style.backgroundColor = "#e5e7eb";
                }
            } else {
                if (errorLop) errorLop.innerText = "";
                if (btnLopSave) btnLopSave.disabled = false;
                if (txtTenLop) {
                    txtTenLop.disabled = false;
                    txtTenLop.style.backgroundColor = "";
                }
            }
        } else {
            if (errorLop) errorLop.innerText = "";
            if (btnLopSave) btnLopSave.disabled = false;
            if (txtTenLop) {
                txtTenLop.disabled = false;
                txtTenLop.style.backgroundColor = "";
            }
        }
    }
}

function checkDuplicateSV() {
    if (currentFormAction === "add_sv") {
        const val = txtMaSV.value.trim();
        const errorSV = document.getElementById("errorSV");
        if (val) {
            const exists = dsSV.some(item => (item.maSV || "").trim().toLowerCase() === val.toLowerCase());
            if (exists) {
                if (errorSV) errorSV.innerText = `Mã sinh viên ${val} đã tồn tại`;
                if (btnDetailSaveForm) btnDetailSaveForm.disabled = true;
                if (txtHoTen) {
                    txtHoTen.disabled = true;
                    txtHoTen.style.backgroundColor = "#e5e7eb";
                }
                if (txtNgaySinh) {
                    txtNgaySinh.disabled = true;
                    txtNgaySinh.style.backgroundColor = "#e5e7eb";
                }
            } else {
                if (errorSV) errorSV.innerText = "";
                if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;
                if (txtHoTen) {
                    txtHoTen.disabled = false;
                    txtHoTen.style.backgroundColor = "";
                }
                if (txtNgaySinh) {
                    txtNgaySinh.disabled = false;
                    txtNgaySinh.style.backgroundColor = "";
                }
            }
        } else {
            if (errorSV) errorSV.innerText = "";
            if (btnDetailSaveForm) btnDetailSaveForm.disabled = false;
            if (txtHoTen) {
                txtHoTen.disabled = false;
                txtHoTen.style.backgroundColor = "";
            }
            if (txtNgaySinh) {
                txtNgaySinh.disabled = false;
                txtNgaySinh.style.backgroundColor = "";
            }
        }
    }
}

if (txtMaLop) {
    ['input', 'change', 'keyup'].forEach(evt => txtMaLop.addEventListener(evt, checkDuplicateLop));
}

if (txtMaSV) {
    ['input', 'change', 'keyup'].forEach(evt => txtMaSV.addEventListener(evt, checkDuplicateSV));
}
'''
js += append_js

with open('static/js/sinhVien_v2.js', 'w', encoding='utf-8') as f:
    f.write(js)

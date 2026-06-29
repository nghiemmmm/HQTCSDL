import re

with open('static/js/sinhVien_v10.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

# Replace the checkDuplicateSV function with the async version
old_check_sv = """
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
"""

new_check_sv = """
async function checkDuplicateSV() {
    if (currentFormAction === "add_sv") {
        const val = txtMaSV.value.trim();
        const errorSV = document.getElementById("errorSV");
        if (val) {
            let exists = dsSV.some(item => (item.maSV || "").trim().toLowerCase() === val.toLowerCase());
            
            if (!exists && val.length >= 3) {
                try {
                    const res = await fetch(`${API_BASE_URL}/sinhvien/${encodeURIComponent(val)}/check-status`);
                    if (res.ok) {
                        exists = true;
                    }
                } catch (e) {
                    console.error("Duplicate check error:", e);
                }
            }

            if (exists) {
                if (errorSV) errorSV.innerText = `Mã sinh viên ${val} đã tồn tại trong hệ thống!`;
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
"""

# Careful string replacement
start_idx = sv_js.find('function checkDuplicateSV() {')
end_idx = sv_js.find('    }\n}', start_idx) + len('    }\n}')
if start_idx != -1 and end_idx != -1:
    sv_js = sv_js[:start_idx] + new_check_sv.strip() + sv_js[end_idx:]

with open('static/js/sinhVien_v11.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v10\.js(\?v=\d+)?', 'sinhVien_v11.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully applied duplicate SV patch.")

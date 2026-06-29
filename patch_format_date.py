import re

with open('static/js/sinhVien_v13.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

# Add formatDateToDMY function
format_date_fn = """
function formatDateToDMY(dateString) {
    if (!dateString) return "";
    const parts = dateString.split("-");
    if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateString;
}
"""

# Insert it at the top (after some initial consts)
sv_js = format_date_fn + "\n" + sv_js

# Replace in renderGridSV
old_tr = "tr.innerHTML = `<td>${sv.maSV}</td><td>${sv.hoTen}</td><td>${sv.ngaySinh}</td>`;"
new_tr = "tr.innerHTML = `<td>${sv.maSV}</td><td>${sv.hoTen}</td><td>${formatDateToDMY(sv.ngaySinh)}</td>`;"
sv_js = sv_js.replace(old_tr, new_tr)

# Replace in viewNgaySinh
old_view = 'viewNgaySinh.textContent = normalizeDateValue(student?.ngaySinh) || "Chua chon";'
new_view = 'viewNgaySinh.textContent = formatDateToDMY(normalizeDateValue(student?.ngaySinh)) || "Chua chon";'
sv_js = sv_js.replace(old_view, new_view)

with open('static/js/sinhVien_v14.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v13\.js(\?v=\d+)?', 'sinhVien_v14.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully patched date format.")

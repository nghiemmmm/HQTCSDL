import re

# 1. Update sinhVien_v5.js -> sinhVien_v6.js
with open('static/js/sinhVien_v5.js', 'r', encoding='utf-8') as f:
    sv_js = f.read()

validation_sv = """
        // Strict Validation
        if (student.maSV.length < 3) {
            alert("Mã sinh viên phải có ít nhất 3 ký tự.");
            return;
        }
        
        const nameWords = student.hoTen.trim().split(/\\s+/);
        if (nameWords.length < 2) {
            alert("Họ tên phải có ít nhất 2 từ.");
            return;
        }
        for (let word of nameWords) {
            if (word.length < 2) {
                alert("Họ tên không hợp lệ (mỗi từ phải có ít nhất 2 chữ cái).");
                return;
            }
        }
        
        const birthDate = new Date(student.ngaySinh);
        const currentDate = new Date();
        let age = currentDate.getFullYear() - birthDate.getFullYear();
        const m = currentDate.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && currentDate.getDate() < birthDate.getDate())) {
            age--;
        }
        if (age < 18) {
            alert("Sinh viên phải đủ 18 tuổi.");
            return;
        }
"""
sv_js = sv_js.replace(
    'if (!student.maSV || !student.hoTen || !student.ngaySinh) {\n\n            alert("Vui lòng nhập đầy đủ thông tin");\n\n            return;\n\n        }',
    'if (!student.maSV || !student.hoTen || !student.ngaySinh) {\n            alert("Vui lòng nhập đầy đủ thông tin");\n            return;\n        }\n' + validation_sv
)

with open('static/js/sinhVien_v6.js', 'w', encoding='utf-8') as f:
    f.write(sv_js)

# 2. Update giaoVien_v5.js -> giaoVien_v6.js
with open('static/js/giaoVien_v5.js', 'r', encoding='utf-8') as f:
    gv_js = f.read()

validation_gv = """
        // Strict Validation
        if (maGV.length < 3) {
            alert("Mã giáo viên phải có ít nhất 3 ký tự.");
            return;
        }
        
        const hoWords = ho.trim().split(/\\s+/);
        for (let word of hoWords) {
            if (word.length < 2) {
                alert("Họ không hợp lệ (mỗi từ phải có ít nhất 2 chữ cái).");
                return;
            }
        }
        
        const tenWords = ten.trim().split(/\\s+/);
        if (tenWords.length > 1) {
            alert("Tên chỉ nên chứa 1 từ (tên chính). Các chữ lót vui lòng nhập vào phần Họ.");
            // We can just allow it but check length
        }
        for (let word of tenWords) {
            if (word.length < 2) {
                alert("Tên không hợp lệ (từ phải có ít nhất 2 chữ cái).");
                return;
            }
        }
"""
gv_js = gv_js.replace(
    'if (!maGV || !ho || !ten) {\n      alert("Vui lòng nhập đầy đủ thông tin bắt buộc (Mã GV, Họ, Tên)!");\n      return;\n    }',
    'if (!maGV || !ho || !ten) {\n      alert("Vui lòng nhập đầy đủ thông tin bắt buộc (Mã GV, Họ, Tên)!");\n      return;\n    }\n' + validation_gv
)

with open('static/js/giaoVien_v6.js', 'w', encoding='utf-8') as f:
    f.write(gv_js)

# 3. Update HTML files to point to v6
with open('templates/formGiaoVien.html', 'r', encoding='utf-8') as f:
    html_gv = f.read()
html_gv = re.sub(r'giaoVien_v5\.js(\?v=\d+)?', 'giaoVien_v6.js', html_gv)
with open('templates/formGiaoVien.html', 'w', encoding='utf-8') as f:
    f.write(html_gv)

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html_sv = f.read()
html_sv = re.sub(r'sinhVien_v5\.js(\?v=\d+)?', 'sinhVien_v6.js', html_sv)
with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(html_sv)

print("Successfully patched JS and HTML for strict validation on save.")

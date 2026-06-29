import sys

with open('static/js/sinhVien.js', 'r', encoding='utf-8') as f:
    content = f.read()

generate_func = """
function generateNextMaSV() {
  if (dsSV.length === 0) return 'SV000001';
  let max = 0;
  for (let i = 0; i < dsSV.length; i++) {
    const masv = dsSV[i].maSV || '';
    if (masv.startsWith('SV')) {
      const num = parseInt(masv.substring(2), 10);
      if (!isNaN(num) && num > max) max = num;
    }
  }
  return 'SV' + String(max + 1).padStart(6, '0');
}

function getFormStudent() {
"""
content = content.replace('function getFormStudent() {', generate_func)

btn_add_old = """        showSinhVienForm();\n\n        if (txtMaSV) txtMaSV.focus();\n\n    };"""
btn_add_new = """        showSinhVienForm();\n\n        if (txtMaSV) {\n            txtMaSV.disabled = true;\n            txtMaSV.style.backgroundColor = '#e5e7eb';\n            txtMaSV.value = generateNextMaSV();\n        }\n\n        if (txtHoTen) txtHoTen.focus();\n\n    };"""
content = content.replace(btn_add_old, btn_add_new)

save_form_old = """        const student = getFormStudent();\n\n        if (!student.maSV || !student.hoTen || !student.ngaySinh) {\n\n            alert("Vui lòng nhập đầy đủ thông tin");\n\n            return;\n\n        }"""
save_form_new = """        const student = getFormStudent();\n        if (currentFormAction !== 'add_sv' && !student.maSV) {\n            alert("Vui lòng nhập mã sinh viên");\n            return;\n        }\n\n        if (!student.hoTen || !student.ngaySinh) {\n\n            alert("Vui lòng nhập đầy đủ thông tin");\n\n            return;\n\n        }"""
content = content.replace(save_form_old, save_form_new)

with open('static/js/sinhVien.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied")

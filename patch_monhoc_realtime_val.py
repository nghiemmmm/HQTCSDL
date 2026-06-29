import re

with open('static/js/monHoc.js', 'a', encoding='utf-8') as f:
    f.write("""

// Real-time validation for duplicate subject code
if (maMHInput) {
    maMHInput.addEventListener('input', function() {
        if (!isThem) return;
        var val = this.value.trim().toUpperCase();
        if (!val) {
            clearError();
            if (btnGhi) { btnGhi.disabled = false; btnGhi.style.opacity = "1"; }
            return;
        }
        
        var exists = data.some(function(item) { 
            return item.maMH && item.maMH.toUpperCase() === val; 
        });
        
        if (exists) {
            showError("Mã môn học đã tồn tại trong danh sách!");
            if (btnGhi) { btnGhi.disabled = true; btnGhi.style.opacity = "0.5"; btnGhi.style.cursor = "not-allowed"; }
        } else {
            clearError();
            if (btnGhi) { btnGhi.disabled = false; btnGhi.style.opacity = "1"; btnGhi.style.cursor = "pointer"; }
        }
    });
}
""")

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=19', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

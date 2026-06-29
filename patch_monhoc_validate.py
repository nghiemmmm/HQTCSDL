import re

with open('static/js/monHoc.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update validate() to check for duplicate maMH
old_validate = """function validate() {
  var ma = maMHInput ? maMHInput.value.trim() : "";
  var ten = tenMHInput ? tenMHInput.value.trim() : "";

  if (isThem && !ma) {
    showError("Vui lAng nh-p MA mA'n h?c.");
    return false;
  }
  if (!ten) {"""
  
new_validate = """function validate() {
  var ma = maMHInput ? maMHInput.value.trim() : "";
  var ten = tenMHInput ? tenMHInput.value.trim() : "";

  if (isThem && !ma) {
    showError("Vui lòng nhập Mã môn học.");
    return false;
  }
  
  if (isThem && ma) {
    var val = ma.toUpperCase();
    var exists = data.some(function(item) { 
      return item.maMH && item.maMH.trim().toUpperCase() === val; 
    });
    if (exists) {
        showError("Mã môn học đã tồn tại trong danh sách!");
        return false;
    }
  }

  if (!ten) {"""

# If there's an encoding issue with the A character, let's use regex
# to safely replace the top of validate
pattern_validate = r'function validate\(\) \{[\s\S]*?if \(!ten\) \{'
replacement_validate = """function validate() {
  var ma = maMHInput ? maMHInput.value.trim() : "";
  var ten = tenMHInput ? tenMHInput.value.trim() : "";

  if (isThem && !ma) {
    showError("Vui lòng nhập Mã môn học.");
    return false;
  }
  
  if (isThem && ma) {
    var val = ma.toUpperCase();
    var exists = data.some(function(item) { 
      return item.maMH && item.maMH.trim().toUpperCase() === val; 
    });
    if (exists) {
        showError("Mã môn học đã tồn tại trong danh sách!");
        return false;
    }
  }

  if (!ten) {"""
js = re.sub(pattern_validate, replacement_validate, js)

# 2. Add .trim() to the real-time event listener as well
js = js.replace('item.maMH.toUpperCase() === val', 'item.maMH.trim().toUpperCase() === val')

with open('static/js/monHoc.js', 'w', encoding='utf-8') as f:
    f.write(js)

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=20', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

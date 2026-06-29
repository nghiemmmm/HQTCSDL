import re

with open('templates/formSinhVien.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The block to remove
block_pattern = re.compile(
    r'<div class="student-detail" id="studentDetailPanel".*?</div>\s*</div>', 
    re.DOTALL
)

new_html = block_pattern.sub('', html)

with open('templates/formSinhVien.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Successfully removed studentDetailPanel.")

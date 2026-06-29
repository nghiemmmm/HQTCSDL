import re

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Change page_title
html = html.replace('{% block page_title %}Mon hoc{% endblock %}', '{% block page_title %}Quản lý môn học{% endblock %}')

# Remove <h2>QUẢN LÝ MÔN HỌC</h2> (case insensitive just in case, but let's use a regex)
# The text might have exact matches
html = re.sub(r'<h2>QUẢN LÝ MÔN HỌC</h2>\s*', '', html)

with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Moved title successfully.")

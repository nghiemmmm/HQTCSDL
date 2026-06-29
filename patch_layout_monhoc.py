import re

with open('templates/formMonHoc.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Extract the components
toolbar_match = re.search(r'(<!-- BUTTON -->.*?</div>\s*)\n\s*<!-- ERROR -->', html, re.DOTALL)
errortext_match = re.search(r'(<!-- ERROR -->.*?</div>\s*)\n\s*<!-- SEARCH -->', html, re.DOTALL)
search_match = re.search(r'(<!-- SEARCH -->.*?</div>\s*)\n\s*<!-- TABLE -->', html, re.DOTALL)

if toolbar_match and errortext_match and search_match:
    toolbar = toolbar_match.group(1)
    errortext = errortext_match.group(1)
    search = search_match.group(1)
    
    # 2. Clean and modify the components
    search_clean = search.replace('style="flex:1;"', 'style="width: 250px;"')
    # Change search outer div margin
    search_clean = re.sub(r'margin:15px 0;', 'margin:0;', search_clean)
    
    # Add margin: 0 to toolbar
    toolbar_clean = toolbar.replace('<div class="toolbar">', '<div class="toolbar" style="margin: 0;">')
    
    # 3. Build the new action bar
    new_layout = f"""{errortext}
  <!-- ACTION BAR -->
  <div class="action-bar" style="display: flex; justify-content: space-between; align-items: center; margin: 15px 0; gap: 20px; flex-wrap: wrap;">
    {search_clean}
    {toolbar_clean}
  </div>
"""
    
    # 4. Replace the old parts
    # First, replace the whole chunk from BUTTON to TABLE with the new layout + TABLE
    chunk_to_replace_match = re.search(r'<!-- BUTTON -->.*?(?=<!-- TABLE -->)', html, re.DOTALL)
    if chunk_to_replace_match:
        html = html[:chunk_to_replace_match.start()] + new_layout + html[chunk_to_replace_match.end():]
        
    # Bump CSS version
    html = re.sub(r'monHoc\.js\?v=\d+', 'monHoc.js?v=12', html)
    html = re.sub(r'monHoc\.css\?v=\d+', 'monHoc.css?v=7', html)

    with open('templates/formMonHoc.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Layout successfully patched.")
else:
    print("Failed to match one of the components.")

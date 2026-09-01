import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Show the sidebar nav items
idx = text.find('class="sidebar-nav"')
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+600])
print(safe)

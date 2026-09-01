import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('class="sidebar"')
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+1500])
print(safe)

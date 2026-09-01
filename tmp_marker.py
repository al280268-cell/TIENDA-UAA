with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
# Find marker
idx = text.find("section-title")
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-30):idx+150])
print(safe)

import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if "function navTo" in l:
        for j in range(i, min(i+25, len(lines))):
            safe = re.sub(r"[^\x00-\x7F]", "?", lines[j].rstrip())
            print(f"{j+1}: {safe[:120]}")
        break

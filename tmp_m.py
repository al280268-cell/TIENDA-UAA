import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("Total lines:", len(lines))
# Show first 20 lines
for i in range(min(20, len(lines))):
    safe = re.sub(r"[^\x00-\x7F]", "?", lines[i].rstrip())
    print(f"{i+1}: {safe[:100]}")

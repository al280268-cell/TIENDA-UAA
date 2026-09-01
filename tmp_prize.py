import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find where prizes are loaded
idx = text.find("/api/rewards")
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-200):idx+600])
print(safe)

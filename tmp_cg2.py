import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("async function createGame()")
# Get more context
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+1200])
print(safe)

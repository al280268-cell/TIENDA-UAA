import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find startGame function
idx = text.find("async function startGame(")
if idx == -1:
    idx = text.find("function startGame(")
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+600])
print(safe)

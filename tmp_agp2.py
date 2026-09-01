import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Show the JS that fills active-game-panel (around pos 42923)
safe = re.sub(r"[^\x00-\x7F]", "?", text[42800:43600])
print(safe)

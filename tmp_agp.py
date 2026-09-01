import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the active-game-panel JS (the one that renders "Partida Actual")
idx = text.find("active-game-panel")
while idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-30):idx+200])
    print(f"--- pos {idx} ---")
    print(safe)
    idx = text.find("active-game-panel", idx+1)

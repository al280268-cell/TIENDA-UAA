import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Find end of dashboard KPI section to inject live panel
# Dashboard section ends around the games table, we want to ADD the live panel after "Crear Partida"
# Find the active-game-panel div
idx = text.find('id="active-game-panel"')
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+500])
print("active-game-panel context:")
print(safe)

import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix _ensure_in_memory to set mission_phase="finished" when status="finished"
old = '''        gs = GameState(
            game_code=code,'''

# Find it
idx = content.find("gs = GameState(")
safe = re.sub(r"[^\x00-\x7F]", "?", content[idx:idx+600])
print(safe)

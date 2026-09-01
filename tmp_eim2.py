import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find _ensure_in_memory
idx = content.find("async def _ensure_in_memory")
safe = re.sub(r"[^\x00-\x7F]", "?", content[idx:idx+1500])
print(safe)

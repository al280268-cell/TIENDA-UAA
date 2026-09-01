import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\rewards.py", "r", encoding="utf-8") as f:
    content = f.read()
safe = re.sub(r"[^\x00-\x7F]", "?", content)
print(safe)

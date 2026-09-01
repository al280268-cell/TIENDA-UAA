import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    content = f.read()
# Find state endpoint
idx = content.find('"/state"')
if idx == -1: idx = content.find("state")
safe = re.sub(r"[^\x00-\x7F]", "?", content[idx:idx+800])
print(safe)

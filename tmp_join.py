import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the join endpoint
idx = content.find("/join")
safe = re.sub(r"[^\x00-\x7F]", "?", content[max(0,idx-30):idx+600])
print(safe)

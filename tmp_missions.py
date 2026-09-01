import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("m1")
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-200):idx+500])
print("Missions config in games.py:")
print(safe)

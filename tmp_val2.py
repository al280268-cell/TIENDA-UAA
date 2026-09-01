import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("def validate")
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+800])
print(safe)

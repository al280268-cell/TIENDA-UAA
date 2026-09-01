import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("phase === 'finished'")
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-50):idx+400])
print(safe)

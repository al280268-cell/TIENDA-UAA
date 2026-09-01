import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\order-confirm.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("window.location")
while idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-50):idx+100])
    print(safe)
    idx = text.find("window.location", idx+1)

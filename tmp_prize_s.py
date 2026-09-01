import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("const S = {")
if idx == -1: idx = text.find("let S =")
if idx == -1: idx = text.find("var S =")
if idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+400])
    print(safe)
else:
    print("S is not defined??")

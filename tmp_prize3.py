import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find countdown-num element
idx = text.find("countdown-num")
while idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-50):idx+200])
    print(f"--- {idx} ---")
    print(safe[:150])
    idx = text.find("countdown-num", idx+1)

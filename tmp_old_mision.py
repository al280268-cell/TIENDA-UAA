import re
with open("old_mision.html", "r", encoding="utf-8") as f:
    text = f.read()

# find store.html
idx = text.find("store.html")
if idx == -1:
    print("store.html not found in old mision.html")
    # try finding "m7" or "tienda"
    idx = text.find("tienda")
    if idx != -1: print(text[max(0,idx-100):idx+300])
else:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+300])
    print(safe)

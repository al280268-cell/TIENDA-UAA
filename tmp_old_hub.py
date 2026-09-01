import re
with open("old_hub.html", "r", encoding="utf-8") as f:
    text = f.read()
idx = text.find("store.html")
if idx == -1:
    print("store.html not found, finding any .html")
    print(re.findall(r"[\w-]+\.html", text))
else:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-200):idx+300])
    print(safe)

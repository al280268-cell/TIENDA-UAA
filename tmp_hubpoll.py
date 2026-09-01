import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the polling function
idx = text.find("async function pollGameState")
if idx == -1: idx = text.find("function pollState")
if idx == -1: idx = text.find("setInterval")
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-30):idx+2000])
print(safe[:2000])

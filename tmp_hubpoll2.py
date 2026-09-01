import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the main poll function and startup
idx = text.find("async function poll(")
if idx == -1: idx = text.find("async function poll ")
if idx == -1:
    # Find the polling loop
    idx = text.find("pollInterval")
    if idx == -1: idx = text.find("setInterval(poll")

safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-200):idx+800])
print("=== POLL FUNCTION ===")
print(safe[:1200])

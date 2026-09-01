import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find _connectLivePolling
idx = text.find("function _connectLivePolling(")
if idx == -1:
    idx = text.find("_connectLivePolling")
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-30):idx+600])
print(safe[:800])

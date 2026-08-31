import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\quiz.py", "r", encoding="utf-8") as f:
    content = f.read()
safe = re.sub(r"[^\x00-\x7F]", "?", content)
# Find the start endpoint
idx = safe.find("def start")
if idx == -1:
    idx = safe.find("/start")
print(safe[max(0,idx-50):idx+300])

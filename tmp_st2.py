import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the GET state endpoint
idx = content.find("@router.get(\"/{code}/state\")")
if idx == -1:
    idx = content.find("/state")
    while idx != -1:
        if "GET" in content[max(0,idx-100):idx] or "router.get" in content[max(0,idx-100):idx]:
            break
        idx = content.find("/state", idx+1)

safe = re.sub(r"[^\x00-\x7F]", "?", content[max(0,idx-50):idx+1000])
print(safe[:1000])

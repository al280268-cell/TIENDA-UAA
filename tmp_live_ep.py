import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\admin.py", "r", encoding="utf-8") as f:
    content = f.read()
# Find the live endpoint
idx = content.find("/live")
safe = re.sub(r"[^\x00-\x7F]", "?", content[max(0,idx-50):idx+400])
print(safe)

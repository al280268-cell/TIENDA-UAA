import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    content = f.read()
idx = content.find("@router.get(\"/{code}/state\")")
end = content.find("\n@router.", idx+10)
safe = re.sub(r"[^\x00-\x7F]", "?", content[idx:end])
print(safe)

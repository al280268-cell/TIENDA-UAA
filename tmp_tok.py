import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find how the token is stored after login
idx = text.find("admin_token")
while idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-60):idx+120])
    print(f"--- {idx} ---")
    print(safe)
    idx = text.find("admin_token", idx+1)

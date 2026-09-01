import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check the state endpoint
idx = content.find('"/state"')
safe = re.sub(r"[^\x00-\x7F]", "?", content[max(0,idx-50):idx+300])
print("state endpoint:")
print(safe)

# Check the create endpoint
idx2 = content.find('"/create"')
safe2 = re.sub(r"[^\x00-\x7F]", "?", content[max(0,idx2-50):idx2+400])
print("\ncreate endpoint:")
print(safe2)

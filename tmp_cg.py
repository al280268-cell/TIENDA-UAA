import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the createGame function and add code to populate live-code field
idx = text.find("async function createGame()")
if idx == -1:
    print("createGame not found")
else:
    # Find return statement in createGame
    end = text.find("return;", idx)
    safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+800])
    print("createGame found:")
    print(safe)

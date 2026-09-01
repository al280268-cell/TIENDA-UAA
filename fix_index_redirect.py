import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the redirect in index.html to go to hub.html instead of lobby.html
if "lobby.html?code=" in text:
    text = text.replace("lobby.html?code=", "hub.html?code=")
    print("Fixed redirect in index.html")
else:
    print("Could not find lobby.html redirect in index.html")

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\index.html", "w", encoding="utf-8") as f:
    f.write(text)

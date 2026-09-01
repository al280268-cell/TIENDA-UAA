import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\store.html", "r", encoding="utf-8") as f:
    text = f.read()

# Let's find script logic
idx = text.find("<script>")
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+1500])
print(safe)

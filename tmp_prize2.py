import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the full loadPrizes function and what happens after
idx = text.find("async function loadPrizes()")
end = text.find("\nasync function ", idx+1)
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:end])
print(safe[:2000])

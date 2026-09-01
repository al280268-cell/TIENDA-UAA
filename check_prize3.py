import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
# Find the JS loading section
for i, l in enumerate(lines):
    if any(x in l for x in ["loadPrizes", "loadRewards", "getRewards", "GET", "rewards", "prizes"]):
        safe = re.sub(r"[^\x00-\x7F]", "?", l.rstrip())
        print(f"{i+1}: {safe[:110]}")

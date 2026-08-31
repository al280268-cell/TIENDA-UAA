import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\results.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("Total lines:", len(lines))
for i, l in enumerate(lines):
    safe = re.sub(r"[^\x00-\x7F]", "?", l.rstrip())
    if any(x in l for x in ["script", "leaderboard", "rank", "podio", "function ", "sessionStorage"]):
        print(f"{i+1}: {safe[:110]}")

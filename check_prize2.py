import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()
# Find where prizes are loaded/rendered
for keyword in ["/api/rewards", "loadRewards", "renderPrize", "prize-card", "stock"]:
    ki = text.find(keyword)
    if ki >= 0:
        safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,ki-50):ki+300])
        print(f"\n=== {keyword} at {ki} ===")
        print(safe)

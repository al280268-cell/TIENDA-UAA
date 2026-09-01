import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()
# Find where it loads rewards
idx = text.find("rewards")
print("Found 'rewards' at:", idx)
# Show area around the fetch/filter
for keyword in ["fetch(", "/api/rewards", "disabled", "filter(", "stock_remaining"]:
    ki = text.find(keyword)
    if ki >= 0:
        print(f"\n--- {keyword} at {ki} ---")
        print(re.sub(r"[^\x00-\x7F]", "?", text[max(0,ki-30):ki+200]))

import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find where the prize JS starts (after DOMContentLoaded or before countdown)
# We want to inject the loadPrizes function before the countdown code
# Look for "let timeLeft = 30"
idx = text.find("let timeLeft = 30")
if idx == -1:
    idx = text.find("// Countdown")
print("Countdown found at:", idx)
print(re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+100]))

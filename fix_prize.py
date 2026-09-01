with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

# The HTML got mangled. Find the prizes-row section and replace it cleanly
import re

# Replacement: dynamic container
new_cards = """  <!-- Prize Cards — loaded dynamically from API -->
  <div class="prizes-row" id="prizes-row">
    <div style="color:rgba(255,255,255,.4);font-size:.9rem;padding:20px">Cargando premios disponibles\u2026</div>
  </div>"""

# Find from "<!-- Prize" to end of </div> of prizes-row
pattern = r'<!--[^>]*Prize Cards[^>]*-->.*?<div class="prizes-row"[^>]*>.*?</div>\s*</div>'
new_text = re.sub(pattern, new_cards, text, flags=re.DOTALL)

if new_text == text:
    print("Pattern not matched, trying manual fix...")
    # Find the malformed section
    start = text.find("<!-- Prize Cards")
    if start == -1:
        start = text.find("prizes-row")
        start = text.rfind("\n", 0, start)  # go to line start

    # Find the success-screen section
    end = text.find("<!-- Success Screen")
    if start > 0 and end > start:
        new_text = text[:start] + new_cards + "\n\n  " + text[end:]
        print(f"Manual replace: {start} to {end}")
    else:
        print(f"Cannot find: start={start}, end={end}")
        exit(1)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "w", encoding="utf-8") as f:
    f.write(new_text)

# Verify
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    verify = f.read()
idx = verify.find("prizes-row")
print("prizes-row at:", idx)
print("Context:", verify[idx-50:idx+200])

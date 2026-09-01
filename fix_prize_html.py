with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the corrupted countdown HTML
bad = '''    <span class="countdown-num" id="countdow      <!-- Prize Cards ? loaded dynamically from API -->
  <div class="prizes-row" id="prizes-row">
    <div style="color:rgba(255,255,255,.4);font-size:.9rem;padding:20px">Cargan'''

# find it approximately  
import re
idx = text.find('id="countdow')
# Get the block from countdown-wrap opening to prizes-row opening
start = text.rfind('<div class="countdown-wrap"', 0, idx)
# Find the end of the malformed block - after prizes-row div opening
end_marker = 'id="prizes-row">'
end_idx = text.find(end_marker, idx)
end_idx = end_idx + len(end_marker)

malformed = text[start:end_idx]
safe_malformed = re.sub(r"[^\x00-\x7F]", "?", malformed)
print("MALFORMED BLOCK:")
print(repr(safe_malformed))
print()

# Replace with correct HTML
fixed = """  <!-- Countdown -->
  <div class="countdown-wrap" id="countdown-wrap">
    <span>&#9201;</span>
    <span>Tiempo para elegir:</span>
    <span class="countdown-num" id="countdown-num">CARGANDO PREMIOS...</span>
  </div>

  <!-- Prize Cards - loaded dynamically from API -->
  <div class="prizes-row" id="prizes-row">"""

text = text[:start] + fixed + text[end_idx:]
print("Fixed! New block:")
print(repr(fixed[:200]))

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Saved OK, len:", len(text))

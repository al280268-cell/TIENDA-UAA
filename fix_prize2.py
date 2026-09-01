import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "r", encoding="utf-8") as f:
    text = f.read()

new_cards = """  <!-- Prize Cards — loaded dynamically from API -->
  <div class="prizes-row" id="prizes-row">
    <div style="color:rgba(255,255,255,.4);font-size:.9rem;padding:20px">Cargando premios...</div>
  </div>"""

# Find the prizes-row block
start = text.find("<!-- Prize Cards")
end = text.find("<!-- Success Screen")

if start > 0 and end > start:
    new_text = text[:start] + new_cards + "\n\n  " + text[end:]
    with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html", "w", encoding="utf-8") as f:
        f.write(new_text)
    with open("verify.txt", "w", encoding="utf-8") as f:
        f.write("OK - len=" + str(len(new_text)))
    print("OK")
else:
    print(f"NOT FOUND: start={start} end={end}")
    # Show what we have around prizes-row
    idx = text.find("prizes-row")
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+400])
    print(safe)

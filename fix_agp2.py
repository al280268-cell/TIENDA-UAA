with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

start = 15596
close = 18424

new_agp = """      <div id="active-game-panel" style="flex:1;">
            <div id="dash-active-status" style="font-size:.85rem;color:rgba(255,255,255,.4);padding:4px 0 8px">
              Sin partida activa
            </div>
          </div>"""

text = text[:start] + new_agp + text[close:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("OK, new len:", len(text))

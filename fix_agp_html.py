with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the active-game-panel in the HTML and replace with simple status div
old_agp_start = '          <div id="active-game-panel" style="flex:1;">'
old_agp_end = '\n        </div>\n\n        <h3 class="section-title"'

si = text.find(old_agp_start)
ei = text.find(old_agp_end, si)

if si == -1 or ei == -1:
    print(f"agp markers not found: si={si} ei={ei}")
    # Try to find it
    idx = text.find('active-game-panel')
    import re
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-50):idx+200])
    print(safe)
    exit(1)

old_agp = text[si:ei]
print("Old agp block length:", len(old_agp))

new_agp = """          <div id="active-game-panel" style="flex:1;">
            <div id="dash-active-status" style="font-size:.85rem;color:rgba(255,255,255,.4);padding:4px 0 8px">
              Sin partida activa
            </div>
          </div>"""

text = text[:si] + new_agp + text[ei:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("active-game-panel simplified OK")

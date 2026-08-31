import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'r', encoding='utf-8') as f:
    text = f.read()

grid_html = r"""<div class="prizes-row" id="prizes-row" style="display:flex; justify-content:center; gap: 16px; width: 100%; max-width: 1000px; margin: 0 auto; flex-wrap: wrap;">
      <div class="prize-card prize-card-ball" id="pc-pelota" onclick="selectPrize('pelota', '⚽ PELOTA DEPORTIVA', '⚽')" style="flex:1; min-width: 200px;">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <span class="prize-emoji" style="font-size:4rem; margin:15px 0; display:block;">⚽</span>
        <div class="prize-name">PELOTA UAA</div>
        <div class="prize-desc">Pelota oficial con logo UAA.</div>
        <button class="btn-prize">ELEGIR PELOTA</button>
      </div>
      <div class="prize-card prize-card-cylinder" id="pc-cilindro" onclick="selectPrize('cilindro', '🥤 CILINDRO UAA', '🥤')" style="flex:1; min-width: 200px;">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <span class="prize-emoji" style="font-size:4rem; margin:15px 0; display:block;">🥤</span>
        <div class="prize-name">CILINDRO UAA</div>
        <div class="prize-desc">Termo deportivo oficial.</div>
        <button class="btn-prize">ELEGIR CILINDRO</button>
      </div>
      <div class="prize-card" id="pc-gallo" onclick="selectPrize('gallo', '🐓 LLAVERO GALLO', '🐓')" style="flex:1; min-width: 200px; background:linear-gradient(135deg,#10B981 0%,#059669 50%,#047857 100%);">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <span class="prize-emoji" style="font-size:4rem; margin:15px 0; display:block;">🐓</span>
        <div class="prize-name">LLAVERO GALLO</div>
        <div class="prize-desc">Llavero metálico oficial de la mascota.</div>
        <button class="btn-prize">ELEGIR LLAVERO</button>
      </div>
      <div class="prize-card" id="pc-stickers" onclick="selectPrize('stickers', '✨ STICKERS UAA', '✨')" style="flex:1; min-width: 200px; background:linear-gradient(135deg,#8B5CF6 0%,#7C3AED 50%,#6D28D9 100%);">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <span class="prize-emoji" style="font-size:4rem; margin:15px 0; display:block;">✨</span>
        <div class="prize-name">STICKERS UAA</div>
        <div class="prize-desc">Paquete de stickers universitarios.</div>
        <button class="btn-prize">ELEGIR STICKERS</button>
      </div>
    </div>"""

text = re.sub(r'<div class="prizes-row" id="prizes-row">.*?</div>\s*<!-- Success screen \(hidden\) -->', grid_html + '\n\n    <!-- Success screen (hidden) -->', text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("HTML Replaced successfully")

import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'r', encoding='utf-8') as f:
    text = f.read()

# I will replace the <div class="prizes-grid">...</div> block
grid_html = r"""<div class="prizes-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; width: 100%; max-width: 900px; margin: 0 auto;">
      <div class="prize-card prize-card-ball" id="pc-pelota" onclick="selectPrize('pelota', '⚽ PELOTA DEPORTIVA', '⚽')" style="min-width: 200px;">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-emoji" style="font-size: 5rem; margin: 20px 0;">⚽</div>
        <div class="prize-name">PELOTA DEPORTIVA</div>
        <div class="prize-desc">Pelota oficial con logo UAA.</div>
        <button class="btn-prize">ELEGIR PELOTA</button>
      </div>

      <div class="prize-card prize-card-cylinder" id="pc-cilindro" onclick="selectPrize('cilindro', '🥤 CILINDRO UAA', '🥤')" style="min-width: 200px;">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-emoji" style="font-size: 5rem; margin: 20px 0;">🥤</div>
        <div class="prize-name">CILINDRO UAA</div>
        <div class="prize-desc">Termo deportivo oficial.</div>
        <button class="btn-prize">ELEGIR CILINDRO</button>
      </div>
      
      <div class="prize-card prize-card-gallo" id="pc-gallo" onclick="selectPrize('gallo', '🐓 LLAVERO DE GALLO', '🐓')" style="min-width: 200px;">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-emoji" style="font-size: 5rem; margin: 20px 0;">🐓</div>
        <div class="prize-name">LLAVERO DE GALLO</div>
        <div class="prize-desc">Llavero metálico oficial.</div>
        <button class="btn-prize">ELEGIR LLAVERO</button>
      </div>

      <div class="prize-card prize-card-stickers" id="pc-stickers" onclick="selectPrize('stickers', '✨ STICKERS UAA', '✨')" style="min-width: 200px;">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-emoji" style="font-size: 5rem; margin: 20px 0;">✨</div>
        <div class="prize-name">STICKERS UAA</div>
        <div class="prize-desc">Stickers universitarios.</div>
        <button class="btn-prize">ELEGIR STICKERS</button>
      </div>
    </div>"""

text = re.sub(r'<div class="prizes-grid">.*?</div>\s*<!-- Botón Continuar -->', grid_html + '\n\n    <!-- Botón Continuar -->', text, flags=re.DOTALL)

js_patch = r"""const prizes = ['pelota', 'cilindro', 'gallo', 'stickers'];
    const rand = prizes[Math.floor(Math.random() * prizes.length)];
    const names = { pelota:'⚽ PELOTA DEPORTIVA', cilindro:'🥤 CILINDRO UAA', gallo:'🐓 LLAVERO DE GALLO', stickers:'✨ STICKERS UAA' };
    const emojis = { pelota:'⚽', cilindro:'🥤', gallo:'🐓', stickers:'✨' };"""

text = re.sub(r'const prizes = \[.*?const emojis = \{[^}]*\};', js_patch, text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated prize.html to show 4 prizes")

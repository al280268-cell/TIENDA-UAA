import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'r', encoding='utf-8') as f:
    text = f.read()

# I will find the section containing the prize cards
start_idx = text.find('<div class="prizes-grid')
if start_idx == -1:
    # Maybe it has a different class? Let's look for 'prize-card-ball'
    start_idx = text.find('<div class="prize-card')
    start_idx = text.rfind('<div', 0, start_idx)

end_idx = text.find('<div class="action-bar">')

if start_idx != -1 and end_idx != -1:
    grid_html = r'''<div class="prizes-grid" style="display:flex; justify-content:center; gap: 16px; width: 100%; max-width: 900px; margin: 0 auto; flex-wrap: wrap;">
      <div class="prize-card prize-card-ball" id="pc-pelota" onclick="selectPrize('pelota', '⚽ PELOTA DEPORTIVA', '⚽')" style="flex:1; min-width: 200px;">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-name" style="font-size:3rem; margin:10px 0;">⚽</div>
        <div class="prize-name">PELOTA UAA</div>
        <div class="prize-desc">Pelota deportiva oficial.</div>
        <button class="btn-prize">ELEGIR PELOTA</button>
      </div>
      <div class="prize-card prize-card-cylinder" id="pc-cilindro" onclick="selectPrize('cilindro', '🥤 CILINDRO UAA', '🥤')" style="flex:1; min-width: 200px; background:linear-gradient(135deg,#3B82F6 0%,#2563EB 50%,#1D4ED8 100%);">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-name" style="font-size:3rem; margin:10px 0;">🥤</div>
        <div class="prize-name">CILINDRO UAA</div>
        <div class="prize-desc">Termo deportivo oficial.</div>
        <button class="btn-prize">ELEGIR CILINDRO</button>
      </div>
      <div class="prize-card" id="pc-gallo" onclick="selectPrize('gallo', '🐓 LLAVERO GALLO', '🐓')" style="flex:1; min-width: 200px; background:linear-gradient(135deg,#10B981 0%,#059669 50%,#047857 100%);">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-name" style="font-size:3rem; margin:10px 0;">🐓</div>
        <div class="prize-name">LLAVERO GALLO</div>
        <div class="prize-desc">Llavero metálico oficial.</div>
        <button class="btn-prize">ELEGIR LLAVERO</button>
      </div>
      <div class="prize-card" id="pc-stickers" onclick="selectPrize('stickers', '✨ STICKERS UAA', '✨')" style="flex:1; min-width: 200px; background:linear-gradient(135deg,#8B5CF6 0%,#7C3AED 50%,#6D28D9 100%);">
        <div class="prize-selected-check">✓</div>
        <span class="prize-exclusive">PREMIO EXCLUSIVO</span>
        <div class="prize-name" style="font-size:3rem; margin:10px 0;">✨</div>
        <div class="prize-name">STICKERS UAA</div>
        <div class="prize-desc">Stickers universitarios.</div>
        <button class="btn-prize">ELEGIR STICKERS</button>
      </div>
    </div>
    '''
    
    new_text = text[:start_idx] + grid_html + text[end_idx:]
    with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Successfully replaced prize cards in HTML.")
else:
    print("Could not find boundaries for replacement.")

import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix updateHUD
patch_hud = r'''
    function updateHUD() {
      const codeEl = document.getElementById('nav-code');
      const nameEl = document.getElementById('nav-name');
      const ptsEl  = document.getElementById('nav-pts');
      
      const pNameEl = document.getElementById('p-name');
      const pScoreEl = document.getElementById('p-score');

      if (codeEl) codeEl.textContent = player.code || 'DEMO';
      if (nameEl) nameEl.textContent = player.name;
      if (ptsEl) ptsEl.textContent = player.pts.toLocaleString();
      
      if (pNameEl) pNameEl.textContent = player.name;
      if (pScoreEl) pScoreEl.textContent = player.pts.toLocaleString() + ' pts';
    }
'''
text = re.sub(r'function updateHUD\(\) \{.*?(?=\n    function renderProgress)', patch_hud.strip(), text, flags=re.DOTALL)

# Fix player.pts logic
patch_points = r'''
        const me = leaderboard.find(p => p.player_id === player.id);
        if (me) {
          player.pts = me.points;
          sessionStorage.setItem('uaa_my_points', me.points);
          updateHUD();
        }
'''
text = re.sub(r'        const me = leaderboard\.find.*?updateHUD\(\);\n        \}', patch_points.strip(), text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed updateHUD and points logic in hub.html")

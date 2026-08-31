import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Add a logout button to the header
header_patch = r'''
    <header class="header">
      <div class="logo">🚀 UAA Hub</div>
      <div style="display:flex; gap:16px; align-items:center;">
          <div class="player-info">
            <span id="p-name">Cargando...</span>
            <div class="score-badge" id="p-score">0 pts</div>
          </div>
          <button onclick="sessionStorage.clear(); window.location.href='/';" style="background:var(--bg); border:1px solid var(--border); color:var(--text); padding:6px 12px; border-radius:6px; cursor:pointer; font-size:12px;">Cerrar Sesión</button>
      </div>
    </header>
'''

text = re.sub(r'<header class="header">.*?</header>', header_patch.strip(), text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

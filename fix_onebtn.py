with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Replace "Iniciar Partida" → calls liveLaunch with that code pre-filled
old_btn = """              ${activeOrWaiting.status === 'waiting' 
                ? `<button class="btn btn-primary btn-sm" onclick="startGame('${gc}')">Iniciar Partida</button>`
                : `<button class="btn btn-danger btn-sm" onclick="endGame('${gc}')">Terminar Partida</button>`
              }"""

new_btn = """              ${activeOrWaiting.status === 'waiting' 
                ? `<button class="btn btn-primary btn-sm" style="font-weight:800" onclick="document.getElementById('live-code').value='${gc}';liveLaunch()">🚀 INICIAR JUEGO</button>`
                : `<button class="btn btn-danger btn-sm" onclick="endGame('${gc}')">Terminar Partida</button>`
              }"""

if old_btn in text:
    text = text.replace(old_btn, new_btn)
    print("Iniciar Partida button replaced OK")
else:
    print("Button text not found exactly, searching...")
    import re
    idx = text.find("Iniciar Partida")
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-100):idx+200])
    print(safe)

# 2. Remove the "Crear Partida" card (old one) from dashboard HTML — 
# replace with just a simpler "INICIAR NUEVO JUEGO" that calls liveLaunch()
old_create = """        <div class="flex gap-4 mb-4 items-center flex-wrap">
          <div class="card" style="flex:1; margin-bottom: 0;">
            <div class="card-header">"""

if old_create in text:
    # Find the end of this create card section
    create_start = text.find(old_create)
    # Find the active-game-panel div which follows
    agp_start = text.find('<div id="active-game-panel"', create_start)
    
    old_create_block = text[create_start:agp_start]
    print("Create block found, length:", len(old_create_block))
    
    # Replace with minimal one-button block
    new_create_block = """        <div class="mb-4">
          <div class="card" style="border:1px solid rgba(230,36,41,.35);margin-bottom:0">
            <div class="card-header" style="color:#FF3B40">🚀 Iniciar Juego Kahoot</div>
            <div style="padding:14px 0;display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end">
              <div>
                <label style="font-size:.72rem;color:var(--text-secondary);display:block;margin-bottom:3px">Seg. por misión</label>
                <input type="number" id="live-duration" value="30" min="10" max="300" style="width:80px">
              </div>
              <div>
                <label style="font-size:.72rem;color:var(--text-secondary);display:block;margin-bottom:3px">Seg. resultados</label>
                <input type="number" id="live-results-sec" value="5" min="3" max="15" style="width:70px">
              </div>
              <div>
                <label style="font-size:.72rem;color:var(--text-secondary);display:block;margin-bottom:3px">Máx. jugadores</label>
                <input type="number" id="dash-max-players" value="30" min="1" max="100" style="width:70px">
              </div>
              <button class="btn btn-danger" style="font-size:1.05rem;font-weight:900;padding:11px 26px;letter-spacing:.5px" onclick="liveLaunch()" id="btn-launch">
                🚀 CREAR E INICIAR JUEGO
              </button>
              <div>
                <div id="live-status-msg" style="font-size:.82rem;color:var(--text-secondary)">
                  Crea la partida y lanza las 6 misiones automáticamente.
                </div>
              </div>
            </div>
          </div>
        </div>

        """
    text = text[:create_start] + new_create_block + text[agp_start:]
    print("Create card replaced OK")
else:
    print("Create card not found")

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Done")

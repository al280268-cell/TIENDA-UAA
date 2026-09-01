with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the live section and replace it completely
start_marker = "<!-- ════ SECTION: CONTROL EN VIVO (Kahoot) ════ -->"
end_marker   = "<!-- ════ SECTION: INVENTARIO v2 ════ -->"

start_idx = text.find(start_marker)
end_idx   = text.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f"Markers not found! start={start_idx} end={end_idx}")
    exit(1)

new_live_section = '''<!-- ════ SECTION: CONTROL EN VIVO (Kahoot) ════ -->
      <section id="sec-live" class="sec-content">
        <div class="flex justify-between items-center mb-4">
          <h2 class="font-display" style="font-size:22px;font-weight:800">🎮 Control en Vivo — Modo Kahoot</h2>
        </div>

        <!-- Setup card -->
        <div class="card mb-4" id="live-setup-card">
          <div class="card-header">Configurar y Lanzar Partida</div>
          <div style="padding:14px 0">
            <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;margin-bottom:16px">
              <div>
                <label style="font-size:.75rem;color:var(--text-secondary);display:block;margin-bottom:4px">Código de partida</label>
                <input type="text" id="live-code" placeholder="Ej: UAA-7CKA" style="max-width:160px;text-transform:uppercase"
                  oninput="this.value=this.value.toUpperCase()">
              </div>
              <div>
                <label style="font-size:.75rem;color:var(--text-secondary);display:block;margin-bottom:4px">Segundos por misión</label>
                <input type="number" id="live-duration" value="30" min="10" max="300" style="max-width:100px">
              </div>
              <div>
                <label style="font-size:.75rem;color:var(--text-secondary);display:block;margin-bottom:4px">Seg. de resultados</label>
                <input type="number" id="live-results-sec" value="5" min="3" max="15" style="max-width:80px">
              </div>
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap">
              <button class="btn btn-primary" style="font-size:1rem;padding:12px 28px;font-weight:800" onclick="liveLaunch()" id="btn-launch">
                🚀 INICIAR JUEGO AUTOMÁTICO
              </button>
              <button class="btn" onclick="liveConnect()" id="btn-connect">
                🔍 Solo ver (ya inició)
              </button>
              <button class="btn btn-danger" onclick="liveEndGame()" id="btn-end-game" style="display:none">
                🏁 Terminar ahora
              </button>
            </div>
            <div id="live-status-msg" style="margin-top:10px;font-size:.85rem;color:var(--text-secondary)"></div>
          </div>
        </div>

        <!-- Live dashboard (only visible when connected) -->
        <div id="live-panel" style="display:none">

          <!-- Status banner -->
          <div id="live-phase-banner" style="border-radius:12px;padding:14px 18px;margin-bottom:16px;font-family:'Bangers',cursive;font-size:1.4rem;letter-spacing:2px;text-align:center;background:rgba(230,36,41,.15);border:1px solid rgba(230,36,41,.35);color:#FF3B40">
            LOBBY — Esperando jugadores
          </div>

          <!-- KPIs -->
          <div class="kpi-grid mb-4" id="live-kpis"></div>

          <!-- Timer + mission info -->
          <div class="card mb-4">
            <div class="card-header">⏱ Misión Actual</div>
            <div style="padding:14px 0;text-align:center">
              <div id="live-timer-display" style="font-size:4rem;font-weight:900;font-family:\'Bangers\',cursive;letter-spacing:4px;color:#E62429;line-height:1">--</div>
              <div style="font-size:.8rem;color:var(--text-secondary);margin-bottom:10px">segundos restantes</div>
              <div id="live-mission-progress" style="height:8px;background:rgba(255,255,255,.08);border-radius:99px;overflow:hidden;max-width:400px;margin:0 auto">
                <div id="live-mission-bar" style="height:100%;background:linear-gradient(90deg,#00E676,#E62429);transition:width 1s linear;width:0%"></div>
              </div>
              <div id="live-mission-label" style="font-size:.85rem;color:var(--text-secondary);margin-top:8px"></div>
            </div>
          </div>

          <!-- Players grid: who answered -->
          <div class="card mb-4">
            <div class="card-header">👥 Jugadores <span id="live-answered-badge" style="font-size:.8rem;font-weight:600;color:var(--text-secondary)"></span></div>
            <div id="live-players-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;padding:12px 0"></div>
          </div>

          <!-- Leaderboard -->
          <div class="card">
            <div class="card-header">🏆 Clasificación en Vivo</div>
            <div id="live-leaderboard" style="padding:8px 0"></div>
          </div>
        </div>
      </section>

      '''

text = text[:start_idx] + new_live_section + text[end_idx:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Live section replaced OK. Length:", len(text))

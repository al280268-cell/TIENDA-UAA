with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Modify liveLaunch to only CREATE the game and connect to it (Lobby mode)
# Add a new function startQuestions to actually trigger the /launch endpoint

idx = text.find("    async function liveLaunch()")
end = text.find("\n    async function liveConnect()", idx)

new_fn = """    async function liveLaunch() {
      const dur = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      _liveDuration = dur;

      function setStatus(msg, isErr) {
        const el = document.getElementById("live-status-msg");
        if (el) el.innerHTML = isErr ? `<span style="color:#E62429;font-weight:700">${msg}</span>` : msg;
      }
      
      const btn = document.getElementById("btn-launch");
      if (btn) { btn.disabled = true; btn.textContent = "Creando sala..."; }
      setStatus("Creando partida nueva (Lobby)\u2026");

      const maxPl = parseInt(document.getElementById("dash-max-players")?.value) || 30;
      const { data: gdata, ok: gok } = await api("POST", "/api/games/create", {
        name: "Feria UAA", max_players: maxPl
      });
      
      if (!gok || !gdata?.game_code) {
        setStatus("Error al crear partida", true);
        if (btn) { btn.disabled = false; btn.textContent = "\\u{1F680} CREAR NUEVA PARTIDA"; }
        return;
      }
      
      _liveCode = gdata.game_code;
      setStatus("\\u2705 Partida " + _liveCode + " creada. Los jugadores ya pueden entrar.");
      if (btn) { btn.disabled = false; btn.textContent = "\\u{1F680} CREAR NUEVA PARTIDA"; }
      
      const endBtn = document.getElementById("btn-end-game");
      if (endBtn) endBtn.style.display = "inline-flex";
      
      // Connect to see players joining
      _connectLivePolling();
    }

    async function startQuestions() {
      if (!_liveCode) {
        showToast("No hay partida activa", "warning");
        return;
      }
      const dur = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      
      const btn = document.getElementById("btn-start-questions");
      if (btn) { btn.disabled = true; btn.textContent = "Arrancando..."; }
      
      const { data, ok } = await api("POST", `/api/games/${_liveCode}/launch`, {
        duration_sec: dur, results_sec: res
      });

      if (!ok) {
        showToast("Error al arrancar preguntas", "error");
        if (btn) { btn.disabled = false; btn.textContent = "\\u25B6\\uFE0F ARRANCAR PREGUNTAS (TODOS LISTOS)"; }
        return;
      }
      
      showToast("¡Preguntas iniciadas!", "success");
      if (btn) { btn.style.display = "none"; } // Hide once started
    }
"""

text = text[:idx] + new_fn + text[end:]

# Now update the UI buttons in the HTML
old_ui = """              <button class="btn btn-danger" style="font-size:1.05rem;font-weight:900;padding:11px 26px;letter-spacing:.5px" onclick="liveLaunch()" id="btn-launch">
                🚀 CREAR E INICIAR JUEGO
              </button>
              <div>
                <div id="live-status-msg" style="font-size:.82rem;color:var(--text-secondary)">
                  Crea la partida y lanza las 6 misiones automáticamente.
                </div>
              </div>"""

new_ui = """              <button class="btn btn-primary" style="font-size:1rem;font-weight:900;padding:11px 20px;" onclick="liveLaunch()" id="btn-launch">
                🚀 CREAR NUEVA PARTIDA (LOBBY)
              </button>
              <div>
                <div id="live-status-msg" style="font-size:.82rem;color:var(--text-secondary)">
                  1. Crea la partida. 2. Espera que los jugadores entren. 3. Arranca las preguntas.
                </div>
              </div>"""
text = text.replace(old_ui, new_ui)

# Add the "ARRANCAR PREGUNTAS" button to the live monitor panel
old_monitor = """        <div id="live-panel" style="display:none;margin-bottom:28px">
          <div id="live-phase-banner" """
new_monitor = """        <div id="live-panel" style="display:none;margin-bottom:28px">
          <div style="text-align:center; margin-bottom:16px;">
            <button class="btn btn-danger" style="font-size:1.2rem;font-weight:900;padding:12px 32px;letter-spacing:1px;box-shadow:0 0 15px rgba(230,36,41,0.5);" onclick="startQuestions()" id="btn-start-questions">
              ▶️ ARRANCAR PREGUNTAS (TODOS LISTOS)
            </button>
          </div>
          <div id="live-phase-banner" """
text = text.replace(old_monitor, new_monitor)

# And hide it if phase is not lobby
old_poll = """        if (phase === 'lobby') {
          banner.textContent = 'LOBBY — Esperando jugadores';
          banner.style.background = 'rgba(43,92,230,.2)';
          banner.style.color = '#64B5F6';"""
new_poll = """        if (phase === 'lobby') {
          banner.textContent = 'LOBBY — Esperando jugadores';
          banner.style.background = 'rgba(43,92,230,.2)';
          banner.style.color = '#64B5F6';
          const sqBtn = document.getElementById('btn-start-questions');
          if (sqBtn) sqBtn.style.display = 'inline-block';
          if (sqBtn) { sqBtn.disabled = false; sqBtn.textContent = "▶️ ARRANCAR PREGUNTAS (TODOS LISTOS)"; }"""
text = text.replace(old_poll, new_poll)

old_poll2 = """        } else if (phase === 'active') {
          banner.textContent = 'MISIÓN ACTIVA';"""
new_poll2 = """        } else if (phase === 'active') {
          const sqBtn = document.getElementById('btn-start-questions');
          if (sqBtn) sqBtn.style.display = 'none';
          banner.textContent = 'MISIÓN ACTIVA';"""
text = text.replace(old_poll2, new_poll2)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Admin HTML modified to separate Create and Launch")

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace liveLaunch + startQuestions with a clean complete version
idx_ll = text.find("    async function liveLaunch()")
idx_lc = text.find("\n    async function liveConnect()", idx_ll)

new_functions = """    // ───────────────────────────────────────────
    // STEP 1: Create lobby (players can join)
    // ───────────────────────────────────────────
    async function liveLaunch() {
      const btn = document.getElementById("btn-launch");
      if (btn) { btn.disabled = true; btn.textContent = "Creando sala..."; }
      
      function setStatus(msg, isErr) {
        const el = document.getElementById("live-status-msg");
        if (el) el.innerHTML = isErr
          ? `<span style="color:#E62429;font-weight:700">\u274c ${msg}</span>`
          : msg;
      }
      setStatus("Creando partida nueva...");

      const maxPl = parseInt(document.getElementById("dash-max-players")?.value) || 30;
      const dur   = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res   = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      _liveDuration = dur;

      const { data, ok } = await api("POST", "/api/games/create", {
        name: "Feria UAA", max_players: maxPl
      });

      if (!ok || !data?.game_code) {
        setStatus(data?.detail || "Error al crear partida", true);
        if (btn) { btn.disabled = false; btn.textContent = "\u{1F680} CREAR NUEVA PARTIDA (LOBBY)"; }
        return;
      }

      _liveCode = data.game_code;
      if (btn) { btn.disabled = false; btn.textContent = "\u{1F680} CREAR NUEVA PARTIDA (LOBBY)"; }

      // Show code big on screen
      showCodeModal(_liveCode);

      setStatus(`\u2705 Sala abierta: <strong style="color:#FFD700;font-size:1.1em">${_liveCode}</strong> &mdash;
        Los jugadores entran en <strong>http://localhost:8000</strong> o <strong>tienda-uaa.onrender.com</strong><br>
        <span style="color:rgba(255,255,255,.5)">Cuando todos est\u00e9n listos, presiona ARRANCAR PREGUNTAS.</span>`);

      // Show the ARRANCAR button and live monitor
      const sqBtn = document.getElementById("btn-start-questions");
      if (sqBtn) { sqBtn.style.display = "inline-block"; sqBtn.disabled = false; }
      const livePanel = document.getElementById("live-panel");
      if (livePanel) livePanel.style.display = "block";
      const endBtn = document.getElementById("btn-end-game");
      if (endBtn) endBtn.style.display = "inline-flex";

      // Start watching players join
      _connectLivePolling();
    }

    // ───────────────────────────────────────────
    // STEP 2: Launch questions (when everyone is in)
    // ───────────────────────────────────────────
    async function startQuestions() {
      if (!_liveCode) { showToast("Primero crea una partida", "warning"); return; }
      const dur = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      const sqBtn = document.getElementById("btn-start-questions");
      if (sqBtn) { sqBtn.disabled = true; sqBtn.textContent = "Arrancando..."; }

      const { data, ok } = await api("POST", `/api/games/${_liveCode}/launch`, {
        duration_sec: dur, results_sec: res
      });

      if (!ok) {
        if (sqBtn) { sqBtn.disabled = false; sqBtn.textContent = "\u25B6\uFE0F ARRANCAR PREGUNTAS"; }
        const el = document.getElementById("live-status-msg");
        if (el) el.innerHTML = `<span style="color:#E62429">\u274c Error: ${data?.detail || "sin respuesta"}</span>`;
        return;
      }

      if (sqBtn) sqBtn.style.display = "none";
      showToast("\u{1F680} \u00a1Preguntas iniciadas! Avanzan solos.", "success");
      const el = document.getElementById("live-status-msg");
      if (el) el.textContent = `\u2705 ${_liveCode} \u2014 ${data.total_missions || 6} misiones \u00d7 ${dur}s \u2014 autom\u00e1ticas`;
    }

"""

text = text[:idx_ll] + new_functions + text[idx_lc:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("OK, len:", len(text))

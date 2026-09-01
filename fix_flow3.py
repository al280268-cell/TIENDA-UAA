import codecs

new_functions = codecs.decode(b"""    // STEP 1: Create lobby
    async function liveLaunch() {
      const btn = document.getElementById("btn-launch");
      if (btn) { btn.disabled = true; btn.textContent = "Creando sala..."; }
      function setStatus(msg, isErr) {
        const el = document.getElementById("live-status-msg");
        if (el) el.innerHTML = isErr ? '<span style="color:#E62429;font-weight:700">' + msg + '</span>' : msg;
      }
      setStatus("Creando partida...");
      const maxPl = parseInt(document.getElementById("dash-max-players")?.value) || 30;
      const dur   = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res   = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      _liveDuration = dur;
      const { data, ok } = await api("POST", "/api/games/create", { name: "Feria UAA", max_players: maxPl });
      if (!ok || !data?.game_code) {
        setStatus((data?.detail || "Error al crear partida"), true);
        if (btn) { btn.disabled = false; btn.textContent = "CREAR NUEVA PARTIDA (LOBBY)"; }
        return;
      }
      _liveCode = data.game_code;
      if (btn) { btn.disabled = false; btn.textContent = "CREAR NUEVA PARTIDA (LOBBY)"; }
      showCodeModal(_liveCode);
      setStatus('Sala abierta: <strong style="color:#FFD700;font-size:1.2em">' + _liveCode + '</strong> &mdash; Jugadores entran en la pagina principal.<br><span style="color:rgba(255,255,255,.5)">Cuando esten todos, presiona ARRANCAR PREGUNTAS.</span>');
      const sqBtn = document.getElementById("btn-start-questions");
      if (sqBtn) { sqBtn.style.display = "inline-block"; sqBtn.disabled = false; }
      const livePanel = document.getElementById("live-panel");
      if (livePanel) livePanel.style.display = "block";
      _connectLivePolling();
    }

    // STEP 2: Launch questions
    async function startQuestions() {
      if (!_liveCode) { showToast("Primero crea una partida", "warning"); return; }
      const dur = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      const sqBtn = document.getElementById("btn-start-questions");
      if (sqBtn) { sqBtn.disabled = true; sqBtn.textContent = "Arrancando..."; }
      const { data, ok } = await api("POST", '/api/games/' + _liveCode + '/launch', { duration_sec: dur, results_sec: res });
      if (!ok) {
        if (sqBtn) { sqBtn.disabled = false; sqBtn.textContent = "ARRANCAR PREGUNTAS"; }
        document.getElementById("live-status-msg").innerHTML = '<span style="color:#E62429">Error: ' + (data?.detail || "sin respuesta") + '</span>';
        return;
      }
      if (sqBtn) sqBtn.style.display = "none";
      showToast("Preguntas iniciadas!", "success");
      document.getElementById("live-status-msg").textContent = _liveCode + ' - ' + (data.total_missions||6) + ' misiones x ' + dur + 's';
    }

""", "utf-8")

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

idx_ll = text.find("    async function liveLaunch()")
idx_lc = text.find("\n    async function liveConnect()", idx_ll)
if idx_ll == -1 or idx_lc == -1:
    print(f"ERROR: ll={idx_ll} lc={idx_lc}")
    exit(1)

text = text[:idx_ll] + new_functions + text[idx_lc:]
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("OK len:", len(text))

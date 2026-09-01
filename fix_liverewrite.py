with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace the liveLaunch function completely with a clean, robust version
idx = text.find("    async function liveLaunch()")
end = text.find("\n    async function liveConnect()", idx)

new_fn = """    async function liveLaunch() {
      // Read inputs with safe fallbacks
      _liveCode = (document.getElementById("live-code")?.value || "").trim().toUpperCase();
      const dur = parseInt(document.getElementById("live-duration")?.value) || 30;
      const res = parseInt(document.getElementById("live-results-sec")?.value) || 5;
      _liveDuration = dur;

      function setStatus(msg, isErr) {
        const el = document.getElementById("live-status-msg");
        if (el) el.innerHTML = isErr ? `<span style="color:#E62429;font-weight:700">${msg}</span>` : msg;
      }
      function setBtnState(loading) {
        const btn = document.getElementById("btn-launch");
        if (!btn) return;
        btn.disabled = loading;
        btn.textContent = loading ? "Iniciando... (max 15s)" : "\\u{1F680} CREAR E INICIAR JUEGO";
      }
      setBtnState(true);
      setStatus("Conectando\u2026");

      // If no code, create a new game first
      if (!_liveCode) {
        setStatus("Creando partida nueva\u2026");
        const maxPl = parseInt(document.getElementById("dash-max-players")?.value) || 30;
        const { data: gdata, ok: gok } = await api("POST", "/api/games/create", {
          name: "Feria UAA", max_players: maxPl
        });
        if (!gok || !gdata?.game_code) {
          setStatus("Error al crear partida: " + (gdata?.detail || "sin respuesta del servidor"), true);
          setBtnState(false);
          return;
        }
        _liveCode = gdata.game_code;
        const inp = document.getElementById("live-code");
        if (inp) inp.value = _liveCode;
        setStatus("Partida creada: " + _liveCode + ". Lanzando misiones\u2026");
      }

      // Launch the game
      const { data, ok } = await api("POST", `/api/games/${_liveCode}/launch`, {
        duration_sec: dur, results_sec: res
      });

      if (!ok) {
        const detail = (data && data.detail) ? data.detail : "Sin respuesta (servidor dormido?)";

        // If game finished, create new one automatically
        if (detail.toLowerCase().includes("finish") || detail.toLowerCase().includes("terminad")) {
          setStatus("Partida ya termino. Creando nueva\u2026");
          const maxPl = parseInt(document.getElementById("dash-max-players")?.value) || 30;
          const { data: nd, ok: nok } = await api("POST", "/api/games/create", {
            name: "Feria UAA", max_players: maxPl
          });
          if (nok && nd?.game_code) {
            _liveCode = nd.game_code;
            const inp = document.getElementById("live-code");
            if (inp) inp.value = _liveCode;
            setStatus("Nueva partida: " + _liveCode + ". Lanzando\u2026");
            const { data: d2, ok: ok2 } = await api("POST", `/api/games/${_liveCode}/launch`, {
              duration_sec: dur, results_sec: res
            });
            if (ok2) {
              _liveTotal = d2.total_missions || 6;
              setStatus("\\u2705 Juego iniciado (" + _liveCode + ") - " + _liveTotal + " misiones x " + dur + "s");
              setBtnState(false);
              document.getElementById("btn-end-game")?.style && (document.getElementById("btn-end-game").style.display = "inline-flex");
              _connectLivePolling();
              return;
            } else {
              setStatus("Error al lanzar nueva partida: " + (d2?.detail || "timeout"), true);
              setBtnState(false);
              return;
            }
          } else {
            setStatus("Error al crear nueva partida: " + (nd?.detail || "timeout"), true);
            setBtnState(false);
            return;
          }
        }

        setStatus("Error: " + detail, true);
        setBtnState(false);
        return;
      }

      // SUCCESS
      _liveTotal = data.total_missions || 6;
      setStatus("\\u2705 Juego iniciado! " + _liveCode + " \\u2014 " + _liveTotal + " misiones x " + dur + "s automaticas");
      setBtnState(false);
      const endBtn = document.getElementById("btn-end-game");
      if (endBtn) endBtn.style.display = "inline-flex";
      _connectLivePolling();
    }
"""

text = text[:idx] + new_fn + text[end:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("liveLaunch completely rewritten OK")

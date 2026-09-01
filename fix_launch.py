with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Find the liveLaunch function and replace it with better version
old_launch = """    async function liveLaunch() {
      _liveCode = (document.getElementById("live-code").value || "").trim().toUpperCase();
      if (!_liveCode) { showToast("Ingresa el código de partida", "warning"); return; }
      const dur  = parseInt(document.getElementById("live-duration").value) || 30;
      const res  = parseInt(document.getElementById("live-results-sec").value) || 5;
      _liveDuration = dur;

      document.getElementById("btn-launch").disabled = true;
      document.getElementById("btn-launch").textContent = "Iniciando\u2026";

      const { data, ok } = await api("POST", `/api/games/${_liveCode}/launch`, {
        duration_sec: dur, results_sec: res
      });

      if (!ok) {
        showToast("Error al iniciar: " + (data?.detail || "verifica el c\u00f3digo"), "error");
        document.getElementById("btn-launch").disabled = false;
        document.getElementById("btn-launch").textContent = "\U0001f680 INICIAR JUEGO AUTOM\u00c1TICO";
        return;
      }
      _liveTotal = data.total_missions || 6;
      showToast("\u00a1Juego iniciado! Avanza autom\u00e1ticamente \U0001f680", "success");
      document.getElementById("live-status-msg").textContent = `\u2705 Juego iniciado \u2014 ${_liveTotal} misiones de ${dur}s cada una`;
      document.getElementById("btn-end-game").style.display = "inline-flex";
      _connectLivePolling();
    }"""

new_launch = """    async function liveLaunch() {
      _liveCode = (document.getElementById("live-code").value || "").trim().toUpperCase();
      const dur  = parseInt(document.getElementById("live-duration").value) || 30;
      const res  = parseInt(document.getElementById("live-results-sec").value) || 5;
      _liveDuration = dur;

      const btnLaunch = document.getElementById("btn-launch");
      btnLaunch.disabled = true;
      btnLaunch.textContent = "Iniciando\u2026";
      document.getElementById("live-status-msg").textContent = "";

      // If no code entered, create a new game automatically
      if (!_liveCode) {
        document.getElementById("live-status-msg").textContent = "Creando partida nueva\u2026";
        const { data: gdata, ok: gok } = await api("POST", "/api/games/create", {
          name: "Feria UAA", max_players: 30
        });
        if (!gok || !gdata?.game_code) {
          showToast("Error al crear partida. Intenta de nuevo.", "error");
          btnLaunch.disabled = false;
          btnLaunch.textContent = "\U0001f680 INICIAR JUEGO AUTOM\u00c1TICO";
          return;
        }
        _liveCode = gdata.game_code;
        document.getElementById("live-code").value = _liveCode;
        // Also update dashboard active panel
        if (typeof Admin !== "undefined") Admin.activeGameCode = _liveCode;
        document.getElementById("live-status-msg").textContent = "Partida creada: " + _liveCode;
        await new Promise(r => setTimeout(r, 500));
      }

      // Launch the game
      const { data, ok } = await api("POST", `/api/games/${_liveCode}/launch`, {
        duration_sec: dur, results_sec: res
      });

      if (!ok) {
        const detail = data?.detail || "error desconocido";
        // If already finished, create a new game and try again
        if (detail.includes("finished") || detail.includes("terminad")) {
          document.getElementById("live-status-msg").textContent = "La partida ya termino. Creando nueva\u2026";
          const { data: nd, ok: nok } = await api("POST", "/api/games/create", {
            name: "Feria UAA", max_players: 30
          });
          if (nok && nd?.game_code) {
            _liveCode = nd.game_code;
            document.getElementById("live-code").value = _liveCode;
            const { data: d2, ok: ok2 } = await api("POST", `/api/games/${_liveCode}/launch`, {
              duration_sec: dur, results_sec: res
            });
            if (ok2) {
              _liveTotal = d2.total_missions || 6;
              showToast("\u00a1Nuevo juego iniciado!", "success");
              document.getElementById("live-status-msg").textContent = `\u2705 Juego ${_liveCode} \u2014 ${_liveTotal} misiones de ${dur}s`;
              document.getElementById("btn-end-game").style.display = "inline-flex";
              btnLaunch.disabled = false;
              btnLaunch.textContent = "\U0001f680 INICIAR JUEGO AUTOM\u00c1TICO";
              _connectLivePolling();
              return;
            }
          }
        }
        showToast("Error: " + detail, "error");
        document.getElementById("live-status-msg").innerHTML = `<span style="color:#E62429">\u274c ${detail}</span>`;
        btnLaunch.disabled = false;
        btnLaunch.textContent = "\U0001f680 INICIAR JUEGO AUTOM\u00c1TICO";
        return;
      }

      _liveTotal = data.total_missions || 6;
      showToast("\u00a1Juego iniciado! \U0001f680", "success");
      document.getElementById("live-status-msg").innerHTML =
        `\u2705 <strong>${_liveCode}</strong> \u2014 ${_liveTotal} misiones \u00d7 ${dur}s + ${res}s resultados`;
      document.getElementById("btn-end-game").style.display = "inline-flex";
      btnLaunch.disabled = false;
      btnLaunch.textContent = "\U0001f680 INICIAR JUEGO AUTOM\u00c1TICO";
      _connectLivePolling();
    }"""

if old_launch in text:
    text = text.replace(old_launch, new_launch)
    print("liveLaunch replaced OK")
else:
    print("OLD launch not found, trying partial match...")
    idx = text.find("async function liveLaunch()")
    print(f"liveLaunch at index: {idx}")
    import re
    safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+300])
    print(safe)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)

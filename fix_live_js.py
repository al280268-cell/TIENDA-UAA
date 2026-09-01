with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find and replace the JS live section
old_js_start = "// ════════════════════════════════════════════════\n    // LIVE CONTROL PANEL (Kahoot)"
old_js_end   = "    // ════════════════════════════════════════════════\n    // INVENTARIO v2"

start_idx = text.find(old_js_start)
end_idx   = text.find(old_js_end)

if start_idx == -1 or end_idx == -1:
    print(f"JS markers not found: start={start_idx} end={end_idx}")
    exit(1)

new_js = '''// ════════════════════════════════════════════════
    // LIVE CONTROL PANEL — Auto Kahoot Mode
    // ════════════════════════════════════════════════
    let _liveInterval = null;
    let _liveCode = "";
    let _liveDuration = 30;
    let _liveTotal = 6;

    async function liveLaunch() {
      _liveCode = (document.getElementById("live-code").value || "").trim().toUpperCase();
      if (!_liveCode) { showToast("Ingresa el código de partida", "warning"); return; }
      const dur  = parseInt(document.getElementById("live-duration").value) || 30;
      const res  = parseInt(document.getElementById("live-results-sec").value) || 5;
      _liveDuration = dur;

      document.getElementById("btn-launch").disabled = true;
      document.getElementById("btn-launch").textContent = "Iniciando…";

      const { data, ok } = await api("POST", `/api/games/${_liveCode}/launch`, {
        duration_sec: dur, results_sec: res
      });

      if (!ok) {
        showToast("Error al iniciar: " + (data?.detail || "verifica el código"), "error");
        document.getElementById("btn-launch").disabled = false;
        document.getElementById("btn-launch").textContent = "🚀 INICIAR JUEGO AUTOMÁTICO";
        return;
      }
      _liveTotal = data.total_missions || 6;
      showToast("¡Juego iniciado! Avanza automáticamente 🚀", "success");
      document.getElementById("live-status-msg").textContent = `✅ Juego iniciado — ${_liveTotal} misiones de ${dur}s cada una`;
      document.getElementById("btn-end-game").style.display = "inline-flex";
      _connectLivePolling();
    }

    async function liveConnect() {
      _liveCode = (document.getElementById("live-code").value || "").trim().toUpperCase();
      if (!_liveCode) { showToast("Ingresa el código", "warning"); return; }
      document.getElementById("live-status-msg").textContent = "Conectado como observador: " + _liveCode;
      document.getElementById("btn-end-game").style.display = "inline-flex";
      _connectLivePolling();
    }

    function _connectLivePolling() {
      document.getElementById("live-panel").style.display = "block";
      livePoll();
      if (_liveInterval) clearInterval(_liveInterval);
      _liveInterval = setInterval(livePoll, 2000);
    }

    async function livePoll() {
      if (!_liveCode) return;
      const { data, ok } = await api("GET", `/api/admin/game/${_liveCode}/live`);
      if (!ok || !data) return;
      renderLivePanel(data);
    }

    function renderLivePanel(d) {
      const round    = d.round_status || {};
      const answered = round.answered || 0;
      const total    = round.total_players || 0;
      const phase    = d.mission_phase || "lobby";
      const mIdx     = d.current_mission_index ?? -1;
      const rem      = d.mission_time_remaining || 0;
      const dur      = d.mission_duration_sec || _liveDuration;
      const totMis   = d.total_missions || _liveTotal;

      // Phase banner
      const bannerEl  = document.getElementById("live-phase-banner");
      const bannerMap = {
        lobby:    { text: "🏟️ LOBBY — Esperando jugadores", bg: "rgba(43,92,230,.2)", border: "rgba(43,92,230,.5)", color: "#64B5F6" },
        active:   { text: `🎯 MISIÓN ${mIdx+1} DE ${totMis} — ${rem}s`, bg: "rgba(230,36,41,.15)", border: "rgba(230,36,41,.4)", color: "#FF3B40" },
        locked:   { text: `⏰ MISIÓN ${mIdx+1} TERMINADA — Mostrando resultados`, bg: "rgba(245,158,11,.15)", border: "rgba(245,158,11,.4)", color: "#F59E0B" },
        finished: { text: "🏆 ¡JUEGO TERMINADO!", bg: "rgba(0,230,118,.1)", border: "rgba(0,230,118,.4)", color: "#00E676" },
      };
      const binfo = bannerMap[phase] || bannerMap.lobby;
      bannerEl.textContent = binfo.text;
      bannerEl.style.background = binfo.bg;
      bannerEl.style.borderColor = binfo.border;
      bannerEl.style.color = binfo.color;

      // KPIs
      document.getElementById("live-kpis").innerHTML = `
        <div class="kpi-card"><div class="kpi-value">${mIdx >= 0 ? mIdx+1 : "—"}/${totMis}</div><div class="kpi-sub">Misión</div></div>
        <div class="kpi-card"><div class="kpi-value">${total}</div><div class="kpi-sub">Jugadores</div></div>
        <div class="kpi-card"><div class="kpi-value">${answered}/${total}</div><div class="kpi-sub">Respondieron</div></div>
        <div class="kpi-card"><div class="kpi-value" style="color:${rem<=10?"#E62429":rem<=20?"#F59E0B":"inherit"}">${rem}s</div><div class="kpi-sub">Tiempo restante</div></div>`;

      // Timer bar
      document.getElementById("live-timer-display").textContent = String(rem).padStart(2,"0");
      const pct = dur > 0 ? Math.max(0, Math.min(100, (rem/dur)*100)) : 0;
      document.getElementById("live-mission-bar").style.width = pct + "%";
      document.getElementById("live-mission-label").textContent =
        phase === "active" ? `Misión ${mIdx+1} de ${totMis} — ID: ${d.current_mission_id || "?"}` :
        phase === "locked" ? `Resultados en pantalla (${d.results_display_sec || 5}s)...` :
        phase === "finished" ? "¡Partida finalizada!" : "Esperando al administrador...";

      // Players
      document.getElementById("live-answered-badge").textContent = `(${answered}/${total} respondieron)`;
      const players = round.player_statuses || [];
      document.getElementById("live-players-grid").innerHTML = players.map(p => {
        const icon   = p.answered ? (p.correct ? "✅" : "❌") : "⏳";
        const bg     = p.answered ? (p.correct ? "rgba(0,230,118,.1)" : "rgba(230,36,41,.08)") : "rgba(255,255,255,.03)";
        const border = p.answered ? (p.correct ? "rgba(0,230,118,.4)" : "rgba(230,36,41,.3)") : "rgba(255,255,255,.08)";
        return `<div style="background:${bg};border:1px solid ${border};border-radius:12px;padding:12px;display:flex;align-items:center;gap:10px">
          <div style="width:34px;height:34px;border-radius:50%;background:${p.avatar_color||"#555"};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.8rem;flex-shrink:0">${p.avatar_initials||"?"}</div>
          <div style="flex:1;min-width:0">
            <div style="font-weight:700;font-size:.9rem">${p.name}</div>
            <div style="font-size:.75rem;color:rgba(240,244,255,.55)">⭐ ${p.points||0} pts · #${p.rank||"—"}</div>
          </div>
          <span style="font-size:1.4rem">${icon}</span>
        </div>`;
      }).join("");

      // Leaderboard
      document.getElementById("live-leaderboard").innerHTML = (d.leaderboard||[]).slice(0,8).map((p,i) => `
        <div style="display:flex;align-items:center;gap:12px;padding:10px 4px;border-bottom:1px solid rgba(255,255,255,.05)">
          <div style="font-weight:900;font-size:1.1rem;min-width:28px;color:${i===0?"#FFD700":i===1?"#C0C0C0":i===2?"#CD7F32":"rgba(240,244,255,.5)"}">${i+1}</div>
          <div style="width:32px;height:32px;border-radius:50%;background:${p.avatar_color||"#555"};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.8rem">${p.avatar_initials||"?"}</div>
          <div style="flex:1;font-weight:700">${p.name}</div>
          <div style="font-weight:800;color:#FFD700">⭐ ${p.points||0}</div>
        </div>`).join("");
    }

    async function liveEndGame() {
      if (!_liveCode || !confirm("¿Terminar la partida ahora?")) return;
      await api("POST", `/api/games/${_liveCode}/end`, {});
      showToast("Partida terminada", "success");
    }

    '''

text = text[:start_idx] + new_js + text[end_idx:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)

print("JS live section replaced OK")

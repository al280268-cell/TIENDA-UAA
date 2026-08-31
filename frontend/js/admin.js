let adminState = {
  token: '',
  selectedGame: null,
  games: [],
  codes: [],
  rewards: []
};

document.addEventListener('DOMContentLoaded', () => {
  const token = App.Session.get('uaa_admin_token');
  if (token) {
    adminState.token = token;
    showDashboard();
  } else {
    showLogin();
  }
  
  document.getElementById('login-btn')?.addEventListener('click', () => {
    const pw = document.getElementById('admin-password').value;
    login(pw);
  });
  
  document.getElementById('create-game-btn')?.addEventListener('click', createGame);
  document.getElementById('create-code-btn')?.addEventListener('click', createCode);
  
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      switchTab(e.target.dataset.tab);
    });
  });
});

function showLogin() {
  document.getElementById('login-section').hidden = false;
  document.getElementById('dashboard-section').hidden = true;
}

function showDashboard() {
  document.getElementById('login-section').hidden = true;
  document.getElementById('dashboard-section').hidden = false;
  loadGames();
  loadRewards();
  loadCodes();
  loadAnalytics();
  setInterval(refreshActiveGame, 5000);
}

async function login(password) {
  const { data, error } = await App.Api.post('/api/admin/login', { password });
  if (error || !data?.admin_token) {
    UI.toast('Contraseña incorrecta', 'error');
    return;
  }
  App.Session.set('uaa_admin_token', data.admin_token);
  App.Session.set('uaa_is_admin', 'true');
  adminState.token = data.admin_token;
  showDashboard();
}

async function createGame() {
  const form = document.getElementById('create-game-form');
  if (!form) return;
  const name = form.querySelector('#game-name').value.trim();
  const difficulty = form.querySelector('input[name="difficulty"]:checked')?.value || 'normal';
  const maxPlayers = parseInt(form.querySelector('#max-players').value || '50');
  const duration = parseInt(form.querySelector('#duration').value || '3');
  const rounds = parseInt(form.querySelector('#rounds').value || '3');
  
  const { data, error } = await App.Api.post('/api/games/create', {
    name, difficulty, max_players: maxPlayers,
    duration_seconds: duration * 60, rounds
  });
  
  if (error) { UI.toast('Error al crear partida', 'error'); return; }
  
  document.getElementById('created-code').textContent = data.game_code;
  document.getElementById('created-code-section').hidden = false;
  
  const lobbyUrl = `${window.location.origin}/frontend/lobby.html?code=${data.game_code}`;
  document.getElementById('lobby-qr').src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(lobbyUrl)}`;
  
  loadGames();
  UI.toast(`Partida ${data.game_code} creada`, 'success');
}

async function loadGames() {
  const { data } = await App.Api.get('/api/admin/games');
  if (data) {
    adminState.games = data;
    renderGamesTable(data);
  }
}

async function selectGame(code) {
  adminState.selectedGame = code;
  const { data } = await App.Api.get(`/api/admin/game/${code}`);
  if (data) {
    renderActiveGame(data);
    switchTab('active');
    document.querySelector('.nav-tab[data-tab="active"]').classList.add('active');
    document.querySelector('.nav-tab[data-tab="games"]').classList.remove('active');
  }
}

async function startGame(code) {
  await App.Api.post(`/api/games/${code}/start`, {});
  UI.toast('¡Competencia iniciada!', 'success');
  refreshActiveGame();
}

async function pauseGame(code) {
  await App.Api.post(`/api/games/${code}/pause`, {});
  UI.toast('Partida pausada', 'warning');
  refreshActiveGame();
}

async function endGame(code) {
  if (!confirm('¿Finalizar partida definitivamente?')) return;
  await App.Api.post(`/api/games/${code}/end`, {});
  UI.toast('Partida finalizada', 'info');
  refreshActiveGame();
}

async function kickPlayer(playerId) {
  if(!adminState.selectedGame) return;
  await App.Api.post('/api/admin/player/kick', { player_id: playerId, game_code: adminState.selectedGame });
  UI.toast('Jugador expulsado', 'warning');
  refreshActiveGame();
}

async function addTime(seconds = 30) {
  if(!adminState.selectedGame) return;
  await App.Api.post('/api/admin/time/add', { game_code: adminState.selectedGame, seconds });
  UI.toast(`+${seconds}s agregados`, 'success');
}

async function triggerSpecialMission() {
  if(!adminState.selectedGame) return;
  await App.Api.post('/api/admin/mission/special', { game_code: adminState.selectedGame });
  UI.toast('¡Misión especial activada!', 'success');
}

async function triggerGlobalEvent(eventType) {
  if(!adminState.selectedGame) return;
  await App.Api.post('/api/events/global', { game_code: adminState.selectedGame, event_type: eventType });
  UI.toast('Evento enviado', 'success');
}

async function loadRewards() {
  const { data } = await App.Api.get('/api/rewards');
  if (data) renderRewardsTable(data);
}

async function createCode() {
  const code = document.getElementById('code-value').value.trim().toUpperCase();
  const points = parseInt(document.getElementById('code-points').value || '100');
  const maxUses = parseInt(document.getElementById('code-max-uses').value || '10');
  const expiresIn = parseInt(document.getElementById('code-expires').value || '60');
  
  if(!code) return UI.toast('Ingresa un código', 'warning');
  
  const { data, error } = await App.Api.post('/api/codes/create', {
    code, reward_points: points, max_uses: maxUses,
    expires_in_minutes: expiresIn, game_code: adminState.selectedGame
  });
  
  if (error) { UI.toast('Error al crear código', 'error'); return; }
  UI.toast(`Código ${data.code} creado`, 'success');
  loadCodes();
}

async function loadCodes() {
  const { data } = await App.Api.get('/api/admin/codes');
  if (data) renderCodesTable(data);
}

async function loadAnalytics() {
  const { data } = await App.Api.get('/api/admin/analytics');
  if (data) renderAnalytics(data);
}

async function refreshActiveGame() {
  if (!adminState.selectedGame) return;
  const { data } = await App.Api.get(`/api/admin/game/${adminState.selectedGame}`);
  if (data) renderActiveGame(data);
}

function renderGamesTable(games) {
  const tbody = document.getElementById('games-tbody');
  if (!tbody) return;
  tbody.innerHTML = games.map(g => `
    <tr>
      <td>${g.code}</td>
      <td>${g.name}</td>
      <td>${g.status}</td>
      <td>${g.players_count}/${g.max_players}</td>
      <td>
        <button onclick="AdminPanel.selectGame('${g.code}')" style="padding:4px 8px; background:#1565C0; color:white; border:none; border-radius:4px; cursor:pointer;">Gestionar</button>
      </td>
    </tr>
  `).join('');
}

function renderActiveGame(game) {
  const container = document.getElementById('active-game-content');
  if (!container) return;
  
  let actions = '';
  if (game.status === 'lobby' || game.status === 'paused') {
    actions += `<button onclick="AdminPanel.startGame('${game.code}')" style="background:#1A7A4A; color:white; padding:8px 16px; border:none; border-radius:4px; margin-right:8px; cursor:pointer;">INICIAR / REANUDAR</button>`;
  }
  if (game.status === 'active') {
    actions += `<button onclick="AdminPanel.pauseGame('${game.code}')" style="background:#C87A00; color:white; padding:8px 16px; border:none; border-radius:4px; margin-right:8px; cursor:pointer;">PAUSAR</button>`;
  }
  actions += `<button onclick="AdminPanel.endGame('${game.code}')" style="background:#C41230; color:white; padding:8px 16px; border:none; border-radius:4px; cursor:pointer;">FINALIZAR</button>`;
  
  let playersHtml = `<table style="width:100%; border-collapse:collapse; margin-top:16px;">
    <thead><tr style="background:#f0f0f0;"><th style="padding:8px; text-align:left;">Jugador</th><th style="padding:8px;">Puntos</th><th style="padding:8px;">Acción</th></tr></thead>
    <tbody>`;
  
  (game.players || []).forEach(p => {
    playersHtml += `
      <tr style="border-bottom:1px solid #eee;">
        <td style="padding:8px;">${p.name}</td>
        <td style="padding:8px; text-align:center;">${p.points || 0}</td>
        <td style="padding:8px; text-align:center;">
          <button onclick="AdminPanel.kickPlayer('${p.id}')" style="background:#C41230; color:white; border:none; padding:4px 8px; border-radius:4px; cursor:pointer;">Expulsar</button>
        </td>
      </tr>
    `;
  });
  playersHtml += `</tbody></table>`;
  
  container.innerHTML = `
    <h2>Partida: ${game.code} - ${game.name}</h2>
    <p><strong>Estado:</strong> ${game.status.toUpperCase()} | <strong>Ronda:</strong> ${game.current_round}/${game.total_rounds} | <strong>Tiempo:</strong> ${App.formatTime(game.time_remaining || 0)}</p>
    <div style="margin-bottom: 24px;">${actions}</div>
    
    <div style="display:flex; gap:8px; margin-bottom: 24px; flex-wrap:wrap;">
      <button onclick="AdminPanel.addTime(30)" style="padding:8px; border:1px solid #ccc; background:white; border-radius:4px; cursor:pointer;">+30s Tiempo</button>
      <button onclick="AdminPanel.triggerSpecialMission()" style="padding:8px; border:1px solid #C87A00; background:#fff3e0; color:#C87A00; font-weight:bold; border-radius:4px; cursor:pointer;">Misión Especial</button>
      <button onclick="AdminPanel.triggerGlobalEvent('double_points')" style="padding:8px; border:1px solid #7A3E9D; background:#f3e5f5; color:#7A3E9D; font-weight:bold; border-radius:4px; cursor:pointer;">Evento 2X Puntos</button>
    </div>
    
    <h3>Jugadores (${(game.players||[]).length})</h3>
    ${playersHtml}
  `;
}

function renderRewardsTable(rewards) {
  const tbody = document.getElementById('rewards-tbody');
  if (!tbody) return;
  tbody.innerHTML = rewards.map(r => `
    <tr>
      <td>${r.emoji} ${r.name}</td>
      <td>${r.stock_remaining}/${r.stock_initial}</td>
      <td>${r.min_points} pts</td>
      <td>${r.min_rank ? '≤ ' + r.min_rank : 'N/A'}</td>
    </tr>
  `).join('');
}

function renderCodesTable(codes) {
  const tbody = document.getElementById('codes-tbody');
  if (!tbody) return;
  tbody.innerHTML = codes.map(c => `
    <tr>
      <td><strong>${c.code}</strong></td>
      <td>${c.reward_points} pts</td>
      <td>${c.uses}/${c.max_uses}</td>
      <td>${c.status}</td>
    </tr>
  `).join('');
}

function renderAnalytics(analytics) {
  const container = document.getElementById('analytics-content');
  if (!container) return;
  container.innerHTML = `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
      <div style="background:#f9f9f9; padding:16px; border-radius:8px; text-align:center;">
        <h3>Partidas Totales</h3>
        <div style="font-size:32px; font-weight:bold; color:#1565C0;">${analytics.total_games || 0}</div>
      </div>
      <div style="background:#f9f9f9; padding:16px; border-radius:8px; text-align:center;">
        <h3>Jugadores Únicos</h3>
        <div style="font-size:32px; font-weight:bold; color:#1A7A4A;">${analytics.total_players || 0}</div>
      </div>
      <div style="background:#f9f9f9; padding:16px; border-radius:8px; text-align:center;">
        <h3>Misiones Completadas</h3>
        <div style="font-size:32px; font-weight:bold; color:#C87A00;">${analytics.missions_completed || 0}</div>
      </div>
      <div style="background:#f9f9f9; padding:16px; border-radius:8px; text-align:center;">
        <h3>Premios Entregados</h3>
        <div style="font-size:32px; font-weight:bold; color:#C41230;">${analytics.rewards_claimed || 0}</div>
      </div>
    </div>
  `;
}

function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(c => c.hidden = true);
  const target = document.getElementById(`tab-${tabName}`);
  if (target) target.hidden = false;
}

window.AdminPanel = {
  createGame, loadGames, selectGame, startGame, pauseGame, endGame,
  kickPlayer, addTime, triggerSpecialMission, triggerGlobalEvent,
  createCode, loadAnalytics
};

// ── Interruptor del Simulador (estado en servidor) ───────────────────────────
async function loadSimulatorState() {
  const stateEl = document.getElementById('sim-state');
  const btn = document.getElementById('sim-toggle');
  const openLink = document.getElementById('sim-open');
  if (!stateEl || !btn) return;
  try {
    const res = await fetch('/api/admin/simulator');
    const data = await res.json();
    renderSimulatorState(!!data.enabled);
  } catch (e) {
    stateEl.textContent = 'error';
  }
}

function renderSimulatorState(enabled) {
  const stateEl = document.getElementById('sim-state');
  const btn = document.getElementById('sim-toggle');
  const openLink = document.getElementById('sim-open');
  stateEl.textContent = enabled ? 'ACTIVADO' : 'DESACTIVADO';
  stateEl.style.color = enabled ? '#10B981' : '#8b93b0';
  btn.textContent = enabled ? 'Desactivar simulador' : 'Activar simulador';
  btn.dataset.enabled = enabled ? '1' : '0';
  if (openLink) openLink.style.display = enabled ? 'inline-block' : 'none';
}

async function toggleSimulator() {
  const btn = document.getElementById('sim-toggle');
  const enabled = btn.dataset.enabled === '1';
  const token = adminState.token || App.Session.get('uaa_admin_token');
  btn.disabled = true;
  try {
    const res = await fetch('/api/admin/simulator', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ enabled: !enabled })
    });
    const data = await res.json();
    renderSimulatorState(!!data.enabled);
  } catch (e) {
    alert('No se pudo cambiar el estado del simulador.');
  } finally {
    btn.disabled = false;
  }
}

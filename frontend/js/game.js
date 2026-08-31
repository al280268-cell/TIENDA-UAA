"use strict";

// ── Global game state (local mirror) ─────────────────────────────────────────
let gameState = {
  gameCode:    '',
  playerId:    '',
  playerName:  '',
  currentRound: 1,
  totalRounds:  5,
  difficulty:   'normal',
  status:       'active',
  isDemo:       false,
};
window.currentRound = 1;

// ── Entry point ───────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  const params = new URLSearchParams(window.location.search);

  // Demo mode
  if (params.get('demo') === '1') {
    gameState.isDemo = true;
    initDemoMode();
    return;
  }

  // Require session
  if (!App.Session.get('uaa_player_token')) {
    App.navigateTo('index.html');
    return;
  }

  // Load session data
  gameState.gameCode   = App.Session.get('uaa_game_code') || '';
  gameState.playerId   = App.Session.get('uaa_player_id') || '';
  gameState.playerName = App.Session.get('uaa_player_name') || 'Jugador';

  if (!gameState.gameCode) {
    App.navigateTo('index.html');
    return;
  }

  // Initialize HUD display
  initDisplay();

  // Fetch initial game state from server
  const { data: gs } = await App.Api.get(`/api/games/${gameState.gameCode}/state`);
  if (gs) {
    gameState.currentRound = gs.current_round || 1;
    gameState.totalRounds  = gs.total_rounds || 5;
    window.currentRound = gameState.currentRound;
    updateRoundIndicator();

    if (gs.time_remaining != null) {
      Timer.startGame(gs.time_remaining, onTimerTick, onTimerExpire);
    }
  }

  // Connect real-time
  const ablyKey = document.querySelector('meta[name="ably-key"]')?.content || '';
  if (ablyKey) {
    RealtimeClient.connect(ablyKey, gameState.gameCode);
  } else {
    RealtimeClient.startPolling(gameState.gameCode);
  }

  // Register real-time handlers
  RealtimeClient.on('score_update',  onScoreUpdate);
  RealtimeClient.on('round_change',  onRoundChange);
  RealtimeClient.on('global_event',  onGlobalEvent);
  RealtimeClient.on('game_paused',   () => { Timer.pauseGame(); showPauseOverlay(true);  });
  RealtimeClient.on('game_resumed',  () => { Timer.resumeGame(); showPauseOverlay(false); });
  RealtimeClient.on('game_ended',    onGameEnded);
  RealtimeClient.on('time_sync',     (d) => { if (d.time_remaining != null) Timer.syncGame(d.time_remaining); });
  RealtimeClient.on('player_kicked', (d) => {
    if (d.player_id === gameState.playerId) {
      UI.toast('Has sido expulsado de la partida', 'error');
      setTimeout(() => App.navigateTo('index.html'), 2000);
    }
  });

  // Sound button
  document.getElementById('sound-btn').addEventListener('click', () => {
    UI.toggleSound();
    document.getElementById('sound-btn').textContent =
      UI.sounds.enabled ? '🔊' : '🔇';
  });

  // Leaderboard poll every 5 seconds (supplement WS)
  setInterval(() => {
    Leaderboard.fetch(gameState.gameCode);
    Leaderboard.myPlayerId = gameState.playerId;
  }, 5000);

  // Load first mission
  await loadMission();
});

// ── Display init ──────────────────────────────────────────────────────────────
function initDisplay() {
  const codeEl = document.getElementById('hud-game-code');
  if (codeEl) codeEl.textContent = gameState.gameCode;

  const nameEl = document.getElementById('my-name-mini');
  if (nameEl) nameEl.textContent = gameState.playerName;

  const avatarEl = document.getElementById('my-avatar-mini');
  if (avatarEl) {
    avatarEl.textContent = App.Session.get('uaa_avatar_initials') || gameState.playerName.substring(0,2).toUpperCase();
    avatarEl.style.background = App.Session.get('uaa_avatar_color') || 'var(--uaa-red)';
  }

  Scoring.currentPoints  = 0;
  Scoring.currentStreak  = 0;
  Scoring.currentRank    = 0;
  Scoring.myPlayerId     = gameState.playerId;
  Scoring.updateHUD();

  Leaderboard.myPlayerId = gameState.playerId;
}

// ── Timer callbacks ───────────────────────────────────────────────────────────
function onTimerTick(remaining) {
  const el = document.getElementById('time-val');
  if (el) el.textContent = Timer.format(remaining);

  const chip = document.getElementById('timer-chip');
  if (chip) {
    chip.classList.toggle('urgent', remaining < 30);
  }

  if (remaining === 10) UI.sounds && UI.sounds.play('tick');
}

function onTimerExpire() {
  UI.showModal({
    emoji: '⏰',
    title: 'TIEMPO AGOTADO',
    message: 'La partida ha terminado.',
    primaryBtn: { text: 'Ver resultados', action: () => App.navigateTo('results.html') }
  });
}

// ── Real-time event handlers ──────────────────────────────────────────────────
function onScoreUpdate(data) {
  // Update leaderboard for all players
  if (data.leaderboard) {
    Leaderboard.update(data.leaderboard);
    Leaderboard.renderMini('lb-mini');
    Leaderboard.renderFull('lb-body');
  }

  // Update my score if it's about me
  if (data.player_id === gameState.playerId) {
    if (data.points !== undefined) {
      const prev = Scoring.currentPoints;
      Scoring.currentPoints = data.points;
      Scoring.animatePoints(prev, data.points);
    }
    if (data.rank !== undefined) {
      const prevRank = Scoring.currentRank;
      Scoring.currentRank = data.rank;
      if (prevRank && prevRank !== data.rank) {
        UI.showRankChange(data.rank, data.rank < prevRank ? 'up' : 'down');
      }
      const miniRank = document.getElementById('my-rank-mini');
      if (miniRank) miniRank.textContent = data.rank;
    }
  }
}

function onRoundChange(data) {
  const newRound = data.round || (gameState.currentRound + 1);
  showRoundModal(newRound, data.leaderboard);
}

function onGlobalEvent(data) {
  UI.showEventBanner(data);
  UI.sounds && UI.sounds.play('event');
}

function onGameEnded(data) {
  Timer.stopGame();

  // Find my result in the leaderboard
  const lb = data.leaderboard || [];
  const mine = lb.find(p => p.player_id === gameState.playerId);

  App.Session.set('uaa_final_rank',        mine?.rank || 0);
  App.Session.set('uaa_final_points',      mine?.points || Scoring.currentPoints);
  App.Session.set('uaa_final_leaderboard', JSON.stringify(lb));

  UI.sounds && UI.sounds.play('victory');
  UI.fireConfetti();

  UI.showModal({
    emoji: '🏁',
    title: '¡COMPETENCIA TERMINADA!',
    message: `Terminaste en el puesto #${mine?.rank || '?'} con ${mine?.points || 0} puntos.`,
    primaryBtn: { text: 'VER RESULTADOS', action: () => App.navigateTo('results.html') }
  });
}

// ── Round complete modal ──────────────────────────────────────────────────────
function showRoundModal(newRound, leaderboard) {
  gameState.currentRound = newRound;
  window.currentRound = newRound;

  const modal = document.getElementById('round-modal');
  const titleEl = document.getElementById('round-modal-title');
  const descEl  = document.getElementById('round-modal-desc');
  const lbEl    = document.getElementById('round-lb-mini');
  const cntEl   = document.getElementById('round-modal-countdown');

  if (titleEl) titleEl.textContent = `RONDA ${newRound - 1} COMPLETADA`;
  if (descEl)  descEl.textContent  = `Comienza la ronda ${newRound} en...`;

  if (lbEl && leaderboard) {
    lbEl.innerHTML = leaderboard.slice(0, 3).map((p, i) => `
      <div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #eee;">
        <strong style="min-width:24px;">${['🥇','🥈','🥉'][i] || (i+1)}</strong>
        ${App.createAvatar(p.avatar_initials, p.avatar_color, 'sm')}
        <span>${p.name}</span>
        <span style="margin-left:auto;font-weight:700;color:var(--uaa-red);">${p.points} pts</span>
      </div>`).join('');
  }

  modal.classList.add('open');

  let secs = 4;
  const tick = setInterval(() => {
    secs--;
    if (cntEl) cntEl.textContent = secs > 0 ? `${secs}...` : '¡COMIENZA!';
    if (secs <= 0) {
      clearInterval(tick);
      modal.classList.remove('open');
      updateRoundIndicator();
      loadMission();
    }
  }, 1000);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function updateRoundIndicator() {
  const el = document.getElementById('round-indicator');
  if (el) el.textContent = `RONDA ${gameState.currentRound} DE ${gameState.totalRounds}`;
}

function showPauseOverlay(show) {
  const el = document.getElementById('pause-overlay');
  if (el) el.style.display = show ? 'flex' : 'none';
}

async function loadMission() {
  const loadingEl = document.getElementById('mission-loading');
  const badge     = document.getElementById('mission-type-badge');
  if (loadingEl) loadingEl.style.display = 'block';
  if (badge)     badge.style.display = 'none';

  const { data, error } = await App.Api.post('/api/missions/generate', {
    player_id:    gameState.playerId,
    game_code:    gameState.gameCode,
    round_number: gameState.currentRound,
  });

  if (loadingEl) loadingEl.style.display = 'none';
  if (badge)     badge.style.display = 'block';

  if (error || !data) {
    UI.toast('Error cargando misión: ' + (error || 'Sin datos'), 'error');
    return;
  }

  Missions.render(data);
}

// ── DEMO MODE ─────────────────────────────────────────────────────────────────
function initDemoMode() {
  // Fill session with demo values
  App.Session.set('uaa_game_code',       'DEMO');
  App.Session.set('uaa_player_id',       'demo-player');
  App.Session.set('uaa_player_name',     'Demo');
  App.Session.set('uaa_avatar_initials', 'DM');
  App.Session.set('uaa_avatar_color',    '#C41230');

  gameState.gameCode   = 'DEMO';
  gameState.playerId   = 'demo-player';
  gameState.playerName = 'Demo';

  initDisplay();

  // Fake game code in header
  const codeEl = document.getElementById('hud-game-code');
  if (codeEl) codeEl.textContent = 'DEMO';

  // Start a fake 5-minute timer
  Timer.startGame(300, onTimerTick, onTimerExpire);

  // Fake leaderboard with bots
  const bots = [
    { player_id:'b1', name:'Bot Azul',  avatar_initials:'BA', avatar_color:'#0B4F8A', points:0, rank:1, streak:0, missions_completed:0, missions_failed:0, status:'connected' },
    { player_id:'b2', name:'Bot Verde', avatar_initials:'BV', avatar_color:'#1A7A4A', points:0, rank:2, streak:0, missions_completed:0, missions_failed:0, status:'connected' },
    { player_id:'b3', name:'Bot Morado',avatar_initials:'BM', avatar_color:'#7A3E9D', points:0, rank:3, streak:0, missions_completed:0, missions_failed:0, status:'connected' },
    { player_id:'demo-player', name:'Tú', avatar_initials:'DM', avatar_color:'#C41230', points:0, rank:4, streak:0, missions_completed:0, missions_failed:0, status:'connected' },
  ];
  Leaderboard.myPlayerId = 'demo-player';
  Leaderboard.update(bots);
  Leaderboard.renderFull('lb-body');
  Leaderboard.renderMini('lb-mini');

  // Bot simulation: every 8-12s a bot gains points
  setInterval(() => {
    bots.forEach(bot => {
      if (bot.player_id !== 'demo-player' && Math.random() < 0.5) {
        const pts = Math.floor(Math.random() * 150) + 50;
        bot.points += pts;
        bot.missions_completed++;
      }
    });
    // Re-sort and update ranks
    bots.sort((a, b) => b.points - a.points);
    bots.forEach((b, i) => b.rank = i + 1);
    Leaderboard.update(bots);
    Leaderboard.renderFull('lb-body');
    Leaderboard.renderMini('lb-mini');

    const me = bots.find(b => b.player_id === 'demo-player');
    const miniRank = document.getElementById('my-rank-mini');
    if (miniRank && me) miniRank.textContent = me.rank;
  }, 9000);

  // Load a demo mission (uses a fake payload)
  const demoMission = {
    mission_id:   'demo-mission-1',
    mission_type: 'detective',
    mission_data: {
      products: [
        { id:'x1', name:'Laptop Gamer Pro', category:'Electrónica', price:18500, rating:4.8, emoji:'💻' },
        { id:'x2', name:'Laptop "Top" REMATE', category:'Electrónica', price:1200, rating:2.1, emoji:'💻' },
        { id:'x3', name:'Laptop Estudio Plus', category:'Electrónica', price:16900, rating:4.5, emoji:'💻' },
      ],
      correct_id: 'x2',
      explanation: 'El precio $1,200 para una laptop es sospechosamente bajo — señal clara de fraude.'
    }
  };
  const loadingEl = document.getElementById('mission-loading');
  if (loadingEl) loadingEl.style.display = 'none';
  const badge = document.getElementById('mission-type-badge');
  if (badge) badge.style.display = 'block';

  Missions.render(demoMission);

  // Intercept Missions.submit in demo mode so it doesn't call the API
  const originalSubmit = Missions.submit.bind(Missions);
  Missions.submit = async function(answer) {
    if (this.answered) return;
    this.answered = true;

    const correct = answer === (this.currentMission?.mission_data?.correct_id || answer);
    const pts     = correct ? 120 : 0;
    const penalty = correct ? 0 : 20;

    document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);

    const fakeResult = {
      correct, points: pts, penalty, total_points: Scoring.currentPoints + pts - penalty,
      streak: correct ? Scoring.currentStreak + 1 : 0,
      explanation: this.currentMission?.mission_data?.explanation || '',
      new_rank: 3
    };

    Scoring.handleMissionResult(fakeResult);

    // Update demo bot "me"
    const me = bots.find(b => b.player_id === 'demo-player');
    if (me) {
      me.points = fakeResult.total_points;
      me.missions_completed += correct ? 1 : 0;
      me.missions_failed    += correct ? 0 : 1;
    }

    UI.toast(correct ? `+${pts} puntos` : `Incorrecto. ${fakeResult.explanation}`, correct ? 'success' : 'error', 2500);

    setTimeout(() => {
      // Next demo mission: find_error
      const errorMission = {
        mission_id:   'demo-mission-2',
        mission_type: 'find_error',
        mission_data: {
          order_data: {
            items: [
              { id:'p3', name:'Termo Inoxidable', emoji:'🥤', price:349 },
              { id:'p8', name:'Mug Cerámica UAA', emoji:'☕', price:129 },
            ],
            subtotal: 478, shipping: 49, total_shown: 599
          },
          correct_total: 527,
          error_description: '349 + 129 + 49 = 527, no 599. El total mostrado tiene un cargo extra no declarado.'
        }
      };
      this.answered = false;
      Missions.render(errorMission);
    }, 2500);
  }.bind(Missions);
}

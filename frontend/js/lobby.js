document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const gameCode = urlParams.get('code') || App.Session.get('uaa_game_code');
  
  if (!gameCode) {
    App.navigateTo('index.html');
    return;
  }
  
  App.Session.set('uaa_game_code', gameCode);
  document.getElementById('display-game-code').textContent = gameCode;
  
  let players = [];
  let isReady = false;
  
  async function loadGameState() {
    const { data } = await App.Api.get(`/api/games/${gameCode}/state`);
    if (data) {
      players = data.players || [];
      renderPlayerList();
      updatePlayerCount();
      
      if (data.status === 'active') {
        App.navigateTo('game.html');
      }
    }
  }
  
  await loadGameState();
  
  const ablyKey = document.querySelector('meta[name="ably-key"]')?.content || '';
  RealtimeClient.connect(ablyKey, gameCode);
  
  RealtimeClient.on('player_joined', (p) => {
    players.push(p);
    renderPlayerList();
    updatePlayerCount();
  });
  
  RealtimeClient.on('player_left', (pId) => {
    players = players.filter(p => p.id !== pId);
    renderPlayerList();
    updatePlayerCount();
  });
  
  RealtimeClient.on('player_ready', (data) => {
    const p = players.find(x => x.id === data.id);
    if (p) p.is_ready = true;
    renderPlayerList();
  });
  
  RealtimeClient.on('player_kicked', (data) => {
    if (data.id === App.Session.get('uaa_player_id')) {
      App.Session.remove('uaa_player_token');
      UI.toast('Has sido expulsado de la partida', 'error');
      setTimeout(() => App.navigateTo('index.html'), 2000);
    } else {
      players = players.filter(p => p.id !== data.id);
      renderPlayerList();
      updatePlayerCount();
    }
  });
  
  RealtimeClient.on('countdown_start', () => {
    UI.showCountdown(() => {
      App.navigateTo('game.html');
    });
  });
  
  RealtimeClient.on('game_started', () => {
    App.navigateTo('game.html');
  });
  
  function renderPlayerList() {
    const list = document.getElementById('lobby-player-list');
    if (!list) return;
    list.innerHTML = players.map(p => `
      <div class="player-item" style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: white; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 12px;">
          ${App.createAvatar(p.initials, p.color, 'sm')}
          <span style="font-weight: bold; font-size: 16px;">${p.name} ${p.id === App.Session.get('uaa_player_id') ? '(Tú)' : ''}</span>
        </div>
        <div>
          ${p.is_ready ? '<span style="background: #1A7A4A; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">LISTO</span>' : '<span style="color: #999; font-size: 12px;">Esperando...</span>'}
          ${App.Session.get('uaa_is_admin') === 'true' ? `<button onclick="kickPlayer('${p.id}')" style="margin-left: 8px; background: #C41230; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 4px 8px;">X</button>` : ''}
        </div>
      </div>
    `).join('');
  }
  
  function updatePlayerCount() {
    const el = document.getElementById('player-count');
    if (el) el.textContent = `${players.length} Jugadores`;
  }
  
  window.kickPlayer = async function(id) {
    if (confirm('¿Expulsar a este jugador?')) {
      await App.Api.post('/api/admin/player/kick', { game_code: gameCode, player_id: id });
    }
  };
  
  const nameInput = document.getElementById('player-name-input');
  if (nameInput && !App.Session.get('uaa_player_token')) {
    document.getElementById('join-section').hidden = false;
    document.getElementById('ready-section').hidden = true;
    
    const colors = ['#C41230', '#1A7A4A', '#0B4F8A', '#7A3E9D', '#C87A00', '#1A6B8A', '#8B1A1A', '#2E7D32', '#1565C0', '#6A1B9A', '#BF360C', '#37474F'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    
    nameInput.addEventListener('input', e => {
      const val = e.target.value.trim();
      const initials = val.substring(0,2).toUpperCase() || '??';
      document.getElementById('avatar-preview').innerHTML = App.createAvatar(initials, randomColor, 'lg');
    });
    
    document.getElementById('join-btn').addEventListener('click', async () => {
      const name = nameInput.value.trim();
      if (!name) return UI.toast('Ingresa tu nombre', 'warning');
      if (players.some(p => p.name.toLowerCase() === name.toLowerCase())) {
        return UI.toast('Ese nombre ya está en uso', 'error');
      }
      
      UI.showLoader('Uniéndose...');
      const { data, error } = await App.Api.post('/api/games/join', {
        game_code: gameCode,
        name: name,
        color: randomColor
      });
      UI.hideLoader();
      
      if (error) return UI.toast(error, 'error');
      
      App.Session.set('uaa_player_token', data.token);
      App.Session.set('uaa_player_id', data.player_id);
      App.Session.set('uaa_player_name', name);
      App.Session.set('uaa_avatar_color', randomColor);
      App.Session.set('uaa_avatar_initials', name.substring(0,2).toUpperCase());
      // Nueva partida: limpia estado de la partida anterior
      ['uaa_match_end','uaa_my_rank','uaa_sim_completed','uaa_sim_completed_order','uaa_cart','uaa_last_order']
        .forEach(k => App.Session.remove(k));
      
      document.getElementById('join-section').hidden = true;
      document.getElementById('ready-section').hidden = false;
    });
  } else {
    document.getElementById('join-section').hidden = true;
    document.getElementById('ready-section').hidden = false;
  }
  
  const readyBtn = document.getElementById('ready-btn');
  if (readyBtn) {
    readyBtn.addEventListener('click', async () => {
      if (isReady) return;
      const { error } = await App.Api.post('/api/players/ready', {
        player_id: App.Session.get('uaa_player_id'),
        game_code: gameCode
      });
      if (error) return UI.toast(error, 'error');
      
      isReady = true;
      readyBtn.disabled = true;
      readyBtn.textContent = '¡ESTÁS LISTO!';
      readyBtn.style.background = '#1A7A4A';
    });
  }
  
  if (App.Session.get('uaa_is_admin') === 'true') {
    const adminControls = document.getElementById('admin-lobby-controls');
    if (adminControls) {
      adminControls.hidden = false;
      document.getElementById('admin-start-btn').addEventListener('click', async () => {
        await App.Api.post(`/api/games/${gameCode}/start`, {});
      });
    }
  }
});


    const player = {
      code:  sessionStorage.getItem('uaa_game_code'),
      id:    sessionStorage.getItem('uaa_player_id'),
      name:  sessionStorage.getItem('uaa_player_name') || 'Jugador',
      pts:   parseInt(sessionStorage.getItem('uaa_my_points') || '0', 10),
      token: sessionStorage.getItem('uaa_player_token'),
      rank:  parseInt(sessionStorage.getItem('uaa_my_rank') || '0', 10),
    };

    // Timer: seed from sessionStorage if server hasn't started yet
    window._timeLeft = parseInt(sessionStorage.getItem('uaa_time_left') || '-1', 10);

    const MISSION_META = {
      ecom_decision:  { icon:'🤔', diff:'MEDIA',   diffClass:'diff-media',   pts:'+150 pts', time:'45s' },
      fraud_detect:   { icon:'🔍', diff:'DIFÍCIL', diffClass:'diff-dificil', pts:'+200 pts', time:'30s' },
      speed_search:   { icon:'⚡', diff:'EXTREMO', diffClass:'diff-extremo', pts:'+250 pts', time:'12s' },
      store_mission:  { icon:'🛒', diff:'ESPECIAL', diffClass:'diff-especial', pts:'+300 pts', time:'libre' },
      checkout_debug: { icon:'🔧', diff:'DIFÍCIL', diffClass:'diff-dificil', pts:'+200 pts', time:'35s' },
      detective:      { icon:'🕵️', diff:'DIFÍCIL', diffClass:'diff-dificil', pts:'+200 pts', time:'30s' },
      best_cart:      { icon:'🛒', diff:'MEDIA',   diffClass:'diff-media',   pts:'+150 pts', time:'45s' },
    };

    async function api(method, url, body) {
      const token = player.token || '';
      try {
        const opts = { method, headers:{'Content-Type':'application/json'} };
        if (token) opts.headers['Authorization'] = 'Bearer ' + token;
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(url, opts);
        const data = await res.json().catch(() => ({}));
        return { data, ok: res.ok };
      } catch(e) { return { data:null, ok:false }; }
    }

    function updateHUD() {
      const stored = parseInt(sessionStorage.getItem('uaa_my_points') || '0', 10);
      if (stored > player.pts) player.pts = stored; // never go lower than stored
      document.getElementById('nav-code').textContent = player.code || '----';
      document.getElementById('nav-name').textContent = player.name;
      document.getElementById('nav-pts').textContent  = player.pts.toLocaleString();
      if (player.rank > 0) document.getElementById('nav-rank').textContent = '#' + player.rank;
    }

    function renderProgress(missions) {
      const done  = missions.filter(m => m.status === 'completed').length;
      const total = missions.length;
      document.getElementById('progress-count').textContent = `${done} / ${total}`;
      const segsEl = document.getElementById('progress-segments');
      segsEl.innerHTML = '';
      missions.forEach(m => {
        const seg = document.createElement('div');
        seg.className = 'prog-seg' + (m.status==='completed'?' done':m.status==='in_progress'?' active':'');
        segsEl.appendChild(seg);
      });
    }

    function renderLeaderboard(board) {
      const cont = document.getElementById('lb-chips');
      cont.innerHTML = '';
      board.forEach((p, i) => {
        const isMe = (p.id || p.player_id) === player.id;
        const rank  = i + 1;
        const rankClass = rank===1?'gold':rank===2?'silver':rank===3?'bronze':'';
        const medal = rank===1?'🥇':rank===2?'🥈':rank===3?'🥉':'#'+rank;
        const color = p.color || p.avatar_color || '#E62429';
        const initials = (p.initials || p.avatar_initials || (p.name||'?')[0]).toUpperCase();
        const pts = p.points ?? 0;

        if (isMe && pts > player.pts) {
          player.pts = pts;
          sessionStorage.setItem('uaa_my_points', pts);
          updateHUD();
        }
        if (isMe) {
          player.rank = rank;
          sessionStorage.setItem('uaa_my_rank', rank);
          document.getElementById('nav-rank').textContent = '#' + rank;
        }

        const chip = document.createElement('div');
        chip.className = `lb-chip${isMe?' me':''}`;
        chip.innerHTML = `
          <div class="lb-chip-avatar" style="background:${color}">${initials}</div>
          <span class="lb-chip-rank ${rankClass}">${medal}</span>
          <span class="lb-chip-name">${p.name}</span>
          <span class="lb-chip-pts">⭐ ${pts}</span>`;
        cont.appendChild(chip);
      });
    }

    let _redirecting = false;
    function goToResults() {
      if (_redirecting) return;
      _redirecting = true;
      window.location.href = 'results.html';
    }

    function renderTimer() {
      const t  = Math.max(0, window._timeLeft ?? 0);
      const el = document.getElementById('nav-timer');
      if (!el) return;
      if (t < 0) { el.textContent = '--:--'; return; }
      const mm = Math.floor(t/60).toString().padStart(2,'0');
      const ss = (t%60).toString().padStart(2,'0');
      el.textContent = `${mm}:${ss}`;
      el.classList.toggle('warn',     t <= 60 && t > 30);
      el.classList.toggle('critical', t <= 30);
      sessionStorage.setItem('uaa_time_left', t);
    }

    async function startMission(id, type, status) {
      if (status === 'completed') return;
      sessionStorage.setItem('uaa_mission_id', id);
      sessionStorage.setItem('uaa_mission_type', type);
      if (player.code && player.id && status === 'available') {
        await api('POST', '/api/missions/start', { player_id:player.id, game_code:player.code, mission_id:id });
      }
      if (type === 'store_mission') window.location.href = 'store.html?mission=' + id;
      else window.location.href = 'game.html?mission=' + id;
    }

    function renderMissions(missions) {
      const grid = document.getElementById('missions-grid');
      grid.innerHTML = '';

      const quizMissions      = missions.filter(m => m.is_quiz);
      const allQuizzesCompleted = quizMissions.length > 0 && quizMissions.every(m => m.status === 'completed');
      const storeMissionObj   = missions.find(m => m.mission_type === 'store_mission');

      // Auto-redirect to store once all quizzes done
      if (allQuizzesCompleted && storeMissionObj && storeMissionObj.status === 'available') {
        const key = 'store_auto_triggered_' + storeMissionObj.mission_id;
        if (!sessionStorage.getItem(key)) {
          sessionStorage.setItem(key, 'true');
          alert('¡Felicidades! Completaste todas las áreas. Ahora entrarás a tu misión final: La Tienda UAA.');
          startMission(storeMissionObj.mission_id, storeMissionObj.mission_type, storeMissionObj.status);
          return;
        }
      }

      missions.forEach((m, i) => {
        const isStore    = m.mission_type === 'store_mission';
        const isQuiz     = m.is_quiz;
        const isDone     = m.status === 'completed';
        const isProgress = m.status === 'in_progress';
        const isLocked   = isStore && !allQuizzesCompleted && !isDone;

        let statusText  = isDone ? 'COMPLETADA' : isProgress ? 'EN PROGRESO' : 'DISPONIBLE';
        let statusClass = isDone ? 'status-completed' : isProgress ? 'status-in-progress' : 'status-available';
        let btnText     = 'INICIAR MISIÓN →';
        let btnClass    = 'btn-start';

        if (isDone)     { btnClass='btn-done';     btnText='✓ COMPLETADA'; }
        if (isProgress) { btnClass='btn-continue'; btnText='CONTINUAR →'; }

        let onclickCode;
        if (isLocked) {
          statusText  = '🔒 BLOQUEADA';
          statusClass = 'status-locked';
          btnText     = '🔒 Completa las áreas';
          btnClass    = 'btn-done';
          onclickCode = `alert('Completa todas las áreas de carrera para desbloquear La Tienda.')`;
        } else if (isStore && !isDone) {
          btnClass    = 'btn-store';
          btnText     = '🛒 ENTRAR A LA TIENDA';
          onclickCode = `(function(){alert('Entrarás al Simulador de E-Commerce de La Tienda UAA. Tu objetivo: explora, agrega productos y completa el checkout.');startMission('${m.mission_id}','${m.mission_type}','${m.status}');})()`;
        } else if (isQuiz) {
          onclickCode = isDone ? '' : `window.location.href='mision.html?mission=${m.mission_id}'`;
        } else {
          onclickCode = isDone ? '' : `startMission('${m.mission_id}','${m.mission_type}','${m.status}')`;
        }

        const cardClass = `mission-card${isDone?' completed':isProgress?' in-progress':''}${isStore?' store-mission':''}`;
        const card = document.createElement('div');
        card.className = cardClass;
        card.style.animationDelay = `${i * 0.07}s`;
        if (isLocked) card.style.opacity = '0.55';

        const footerPts  = isQuiz ? '+150 pts aprox.' : (MISSION_META[m.mission_type]?.pts || '+150 pts');
        const footerTime = isQuiz ? `${m.num_questions} preguntas` : (MISSION_META[m.mission_type]?.time || 'Libre');
        const titleText  = isQuiz ? `${m.emoji || ''} ${m.area}` : (m.title || 'La Tienda');
        const topicText  = isQuiz ? 'ÁREA DE LA CARRERA' : (m.topic || 'CUSTOMER JOURNEY');
        const diffBadge  = isQuiz ? '<span class="diff-badge diff-media">MEDIA</span>' : `<span class="diff-badge ${MISSION_META[m.mission_type]?.diffClass || 'diff-especial'}">${MISSION_META[m.mission_type]?.diff || 'ESPECIAL'}</span>`;

        card.innerHTML = `
          <div class="card-top">
            <div style="flex:1">
              <div class="mission-title">${titleText}</div>
              <div class="mission-topic">${topicText}</div>
            </div>
            <div class="card-badges">
              <span class="status-badge ${statusClass}">${statusText}</span>
              ${diffBadge}
            </div>
          </div>
          <div class="mission-desc">${isQuiz ? 'Demuestra tus conocimientos y capacidad en esta área de la carrera.' : (m.desc || 'Navega por la tienda real y completa el checkout.')}</div>
          <div class="card-footer">
            <span class="pts-badge">⭐ ${footerPts}</span>
            <span class="time-badge">⏱ ${footerTime}</span>
          </div>
          <button class="btn-mission ${btnClass}" ${isDone && !isStore ? 'disabled' : ''} onclick="${onclickCode}">${btnText}</button>
        `;
        grid.appendChild(card);
      });
    }

    async function loadData() {
      let missions = [];

      if (player.code && player.id) {
        let storeMission = null;

        // 1. Get store mission
        try {
          const mRes = await api('GET', `/api/missions/pool/${player.code}/${player.id}`);
          if (mRes.ok && mRes.data?.missions) {
            storeMission = mRes.data.missions.find(m => m.mission_type === 'store_mission');
          }
        } catch(e) {}

        // 2. Get quiz missions
        try {
          const qRes = await api('GET', `/api/quiz/missions/${player.code}/${player.id}`);
          if (qRes.ok && qRes.data?.missions) {
            missions = qRes.data.missions.map(m => ({ ...m, is_quiz: true }));
          }
        } catch(e) {}

        if (storeMission) missions.push(storeMission);

        // 3. Leaderboard — opportunistic sync
        try {
          const lRes = await api('GET', `/api/scoring/leaderboard/${player.code}`);
          if (lRes.ok && Array.isArray(lRes.data) && lRes.data.length > 0) {
            renderLeaderboard(lRes.data);
          } else {
            // Build a local chip from sessionStorage so the UI is never empty
            renderLeaderboard([{
              id: player.id, player_id: player.id,
              name: player.name, points: player.pts,
              avatar_color: '#E62429',
              avatar_initials: (player.name[0] || 'J').toUpperCase()
            }]);
          }
        } catch(e) {}

        // 4. Timer from server
        try {
          const sRes = await api('GET', `/api/games/${player.code}/state`);
          if (sRes.ok && sRes.data) {
            const tr = sRes.data.time_remaining;
            if (tr !== null && tr !== undefined && tr >= 0) {
              window._timeLeft = tr;
              renderTimer();
              if (sRes.data.status === 'finished' || tr <= 0) goToResults();
            }
          }
        } catch(e) {}

        // 5. Re-sync points from sessionStorage (never overwrite with lower value)
        const stored = parseInt(sessionStorage.getItem('uaa_my_points') || '0', 10);
        if (stored > player.pts) { player.pts = stored; }
        updateHUD();
      }

      renderProgress(missions);
      renderMissions(missions);
    }

    async function init() {
      updateHUD();
      await loadData();
      setInterval(loadData, 5000);
      // Local countdown tick
      setInterval(() => {
        if (window._timeLeft > 0) {
          window._timeLeft--;
          renderTimer();
        }
      }, 1000);
    }

    init();
  
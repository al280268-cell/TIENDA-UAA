import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove the banner
banner_regex = r'<a href="mision\.html".*?</a>'
text = re.sub(banner_regex, '', text, flags=re.DOTALL)

# 2. Replace everything from renderMissions to init
unified_patch = r"""
    function renderMissions(missions) {
      const grid = document.getElementById('missions-grid');
      grid.innerHTML = '';
      
      let completedCount = 0;
      
      missions.forEach((m, i) => {
        const isStore = m.mission_type === 'store_mission';
        const isQuiz = m.is_quiz;
        const isDone = m.status === 'completed';
        const isProgress = m.status === 'in_progress';
        
        if(isDone) completedCount++;

        const statusText  = isDone ? 'COMPLETADA' : isProgress ? 'EN PROGRESO' : 'DISPONIBLE';
        const statusClass = isDone ? 'status-completed' : isProgress ? 'status-in-progress' : 'status-available';

        let btnClass = 'btn-start', btnText = 'INICIAR MISIÓN →';
        if (isDone)     { btnClass='btn-done';     btnText='✓ COMPLETADA'; }
        if (isProgress) { btnClass='btn-continue'; btnText='CONTINUAR MISIÓN →'; }
        
        if (isStore) {
          btnText = isDone ? '✓ COMPLETADA' : 'ENTRAR A LA TIENDA →';
          if(!isDone) btnClass = 'btn-store';
        }

        const card = document.createElement('div');
        card.className = `mission-card${isDone?' completed':isProgress?' in-progress':''}${isStore?' store-mission':''}`;
        card.style.animationDelay = `${i * 0.08}s`;
        
        if (isQuiz) {
          card.innerHTML = `
            <div class="mission-header">
              <div class="mission-title">
                <span class="mission-icon" style="background:var(--card-bg);">${m.emoji}</span>
                ${m.area}
              </div>
              <div class="mission-status ${statusClass}">${statusText}</div>
            </div>
            <div class="mission-type">ÁREA DE LA CARRERA</div>
            <p class="mission-desc">Demuestra tus conocimientos en ${m.area}.</p>
            <div class="mission-stats">
              <span class="stat-pts">+150 pts aprox.</span>
              <span class="stat-time">⏱ ${m.num_questions} preguntas</span>
            </div>
            <button class="${btnClass}" onclick="window.location.href='mision.html?mission=${m.mission_id}'">${btnText}</button>
          `;
        } else {
          const meta = MISSION_META[m.mission_type] || { icon:'🛒', diff:'ESPECIAL', diffClass:'diff-media', pts:'+150 pts', time:'Libre' };
          card.innerHTML = `
            <div class="mission-header">
              <div class="mission-title">
                <span class="mission-icon" style="background:var(--card-bg);">${meta.icon}</span>
                ${m.title || meta.title || 'La Tienda'}
              </div>
              <div class="mission-status ${statusClass}">${statusText}</div>
            </div>
            <div class="mission-type">${m.topic || meta.topic || 'CUSTOMER JOURNEY'} <span style="float:right;" class="${meta.diffClass}">${meta.diff}</span></div>
            <p class="mission-desc">${m.desc || meta.desc || 'Navega por la tienda real, agrega productos al carrito y completa el checkout.'}</p>
            <div class="mission-stats">
              <span class="stat-pts">${meta.pts}</span>
              <span class="stat-time">⏱ ${meta.time}</span>
            </div>
            <button class="${btnClass}" onclick="window.location.href='game.html?mission=${m.mission_id}'">${btnText}</button>
          `;
        }
        grid.appendChild(card);
      });
      
      const pb = document.getElementById('progress-bar-fill');
      const pt = document.getElementById('progress-text');
      if(pb && pt && missions.length > 0) {
          const pct = Math.round((completedCount / missions.length) * 100);
          pb.style.width = pct + '%';
          pt.textContent = `${completedCount} / ${missions.length} completadas`;
          
          if (completedCount === missions.length) {
              const overlay = document.getElementById('completion-overlay');
              if(overlay) {
                  overlay.classList.add('active');
                  const bar = document.getElementById('co-bar');
                  setTimeout(() => { bar.style.transition='width 3s ease'; bar.style.width='100%'; }, 100);
                  setTimeout(() => { window.location.href = 'results.html'; }, 3500);
              }
          }
      }
    }

    async function startMission(id, type, status) {
        // Fallback for store_mission from hub.html
        if (status === 'completed') return;
        window.location.href = 'game.html?mission=' + id;
    }

    async function loadData() {
      let missions   = [];
      let allComplete = false;

      if (player.code && player.id) {
        let storeMission = null;
        try {
          const mRes = await api('GET', `/api/missions/pool/${player.code}/${player.id}`);
          if (mRes.ok && mRes.data && mRes.data.missions) {
            storeMission = mRes.data.missions.find(m => m.mission_type === 'store_mission');
          }
        } catch(e) {}

        try {
          const qRes = await api('GET', `/api/quiz/missions/${player.code}/${player.id}`);
          if (qRes && qRes.missions) {
            missions = qRes.missions.map(m => ({
              ...m,
              is_quiz: true
            }));
          }
        } catch(e) {}

        if(storeMission) missions.push(storeMission);

        const lRes = await api('GET', `/api/scoring/leaderboard/${player.code}`);
        let leaderboard = MOCK_LEADERBOARD;
        if (lRes.ok && lRes.data && lRes.data.leaderboard) leaderboard = lRes.data.leaderboard;
        renderLeaderboard(leaderboard);

        const sRes = await api('GET', `/api/games/${player.code}/state`);
        if (sRes.ok && sRes.data && sRes.data.time_remaining !== undefined) {
          window._timeLeft = sRes.data.time_remaining;
          renderTimer();
          if (sRes.data.status === 'finished' || sRes.data.time_remaining <= 0) {
            goToResults();
          }
        }

        const me = leaderboard.find(p => p.player_id === player.id);
        if (me) {
          player.score = me.points;
          sessionStorage.setItem('uaa_player', JSON.stringify(player));
          updateHUD();
        }
      }

      renderMissions(missions);
    }
"""

text = re.sub(r'    function renderMissions\(missions\) \{.*?(?=async function init\(\))', unified_patch.strip() + '\n\n    ', text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Hub completely fixed!")

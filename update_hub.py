import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove the banner
banner_regex = r'<a href="mision\.html".*?</a>'
text = re.sub(banner_regex, '', text, flags=re.DOTALL)

# 2. Modify loadData to fetch both and combine
load_data_patch = r"""
    async function loadData() {
      let missions   = [];
      let allComplete = false;

      if (player.code && player.id) {
        // Fetch Store Mission from old API
        let storeMission = null;
        try {
          const mRes = await api('GET', /api/missions/pool//);
          if (mRes.ok && mRes.data && mRes.data.missions) {
            storeMission = mRes.data.missions.find(m => m.mission_type === 'store_mission');
          }
        } catch(e) {}

        // Fetch Career Areas from new API
        try {
          const qRes = await api('GET', /api/quiz/missions//);
          if (qRes && qRes.missions) {
            missions = qRes.missions.map(m => ({
              ...m,
              is_quiz: true // mark as career area
            }));
          }
        } catch(e) {}

        if(storeMission) missions.push(storeMission);

        // Leaderboard & State
        const lRes = await api('GET', /api/scoring/leaderboard/);
        let leaderboard = MOCK_LEADERBOARD;
        if (lRes.ok && lRes.data && lRes.data.leaderboard) leaderboard = lRes.data.leaderboard;
        renderLeaderboard(leaderboard);

        const sRes = await api('GET', /api/games//state);
        if (sRes.ok && sRes.data?.time_remaining !== undefined) {
          window._timeLeft = sRes.data.time_remaining;
          renderTimer();
          if (sRes.data.status === 'finished' || sRes.data.time_remaining <= 0) {
            goToResults();
          }
        }

        // Try to get rank
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

text = re.sub(r'async function loadData\(\) \{.*?(?=function renderLeaderboard)', load_data_patch.strip() + '\n\n    ', text, flags=re.DOTALL)

# 3. Modify renderMissions
render_missions_patch = r"""
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
        card.className = mission-card;
        card.style.animationDelay = ${i * 0.08}s;
        
        if (isQuiz) {
          // Render Career Area Card
          card.innerHTML = 
            <div class="mission-header">
              <div class="mission-title">
                <span class="mission-icon" style="background:var(--card-bg);"></span>
                
              </div>
              <div class="mission-status "></div>
            </div>
            <div class="mission-type">ÁREA DE LA CARRERA</div>
            <p class="mission-desc">Demuestra tus conocimientos en .</p>
            <div class="mission-stats">
              <span class="stat-pts">+150 pts aprox.</span>
              <span class="stat-time">⏱  preguntas</span>
            </div>
            <button class="" onclick="window.location.href='mision.html?mission='"></button>
          ;
        } else {
          // Render Store Card (or fallback old cards)
          const meta = MISSION_META[m.mission_type] || { icon:'🛒', diff:'ESPECIAL', diffClass:'diff-media', pts:'+150 pts', time:'Libre' };
          card.innerHTML = 
            <div class="mission-header">
              <div class="mission-title">
                <span class="mission-icon" style="background:var(--card-bg);"></span>
                
              </div>
              <div class="mission-status "></div>
            </div>
            <div class="mission-type"> <span style="float:right;" class=""></span></div>
            <p class="mission-desc"></p>
            <div class="mission-stats">
              <span class="stat-pts"></span>
              <span class="stat-time">⏱ </span>
            </div>
            <button class="" onclick="window.location.href='game.html?mission='"></button>
          ;
        }
        grid.appendChild(card);
      });
      
      // Update progress bar
      const pb = document.getElementById('progress-bar-fill');
      const pt = document.getElementById('progress-text');
      if(pb && pt && missions.length > 0) {
          const pct = Math.round((completedCount / missions.length) * 100);
          pb.style.width = pct + '%';
          pt.textContent = ${completedCount} /  completadas;
          
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
"""

text = re.sub(r'    function renderMissions\(missions\) \{.*?(?=async function init\(\))', render_missions_patch.strip() + '\n\n    ', text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Hub.html rewritten!")

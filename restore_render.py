import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

render_missions_patch = r"""
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
      
      let completedCount = 0;
      const quizMissions = missions.filter(m => m.is_quiz);
      const quizzesDone = quizMissions.filter(m => m.status === 'completed').length;
      const allQuizzesCompleted = (quizMissions.length > 0 && quizzesDone === quizMissions.length);
      
      const storeMissionObj = missions.find(m => m.mission_type === 'store_mission');
      if (allQuizzesCompleted && storeMissionObj && storeMissionObj.status === 'available') {
          if (!sessionStorage.getItem('store_auto_triggered_' + storeMissionObj.mission_id)) {
              sessionStorage.setItem('store_auto_triggered_' + storeMissionObj.mission_id, 'true');
              console.log("Auto-redirecting to Store Mission...");
              startMission(storeMissionObj.mission_id, storeMissionObj.mission_type, storeMissionObj.status);
              return;
          }
      }
      
      missions.forEach((m, i) => {
        const isStore = m.mission_type === 'store_mission';
        const isQuiz = m.is_quiz;
        const isDone = m.status === 'completed';
        const isProgress = m.status === 'in_progress';
        
        if(isDone) completedCount++;

        let statusText  = isDone ? 'COMPLETADA' : isProgress ? 'EN PROGRESO' : 'DISPONIBLE';
        let statusClass = isDone ? 'status-completed' : isProgress ? 'status-in-progress' : 'status-available';

        let btnClass = 'btn-start', btnText = 'INICIAR MISIÓN →';
        if (isDone)     { btnClass='btn-done';     btnText='✓ COMPLETADA'; }
        if (isProgress) { btnClass='btn-continue'; btnText='CONTINUAR MISIÓN →'; }
        
        let clickAction = isQuiz ? `window.location.href='mision.html?mission=${m.mission_id}'` : `startMission('${m.mission_id}', '${m.mission_type}', '${m.status}')`;
        let cardStyle = '';

        if (isStore) {
          if (!allQuizzesCompleted) {
             statusText = 'BLOQUEADA';
             statusClass = 'status-completed';
             btnText = '🔒 BLOQUEADA';
             btnClass = 'btn-done';
             clickAction = "alert('Debes completar todas las misiones de las Áreas de la Carrera para desbloquear La Tienda.')";
             cardStyle = 'opacity: 0.65; filter: grayscale(0.8);';
          } else {
             btnText = isDone ? '✓ COMPLETADA' : 'ENTRAR A LA TIENDA →';
             if(!isDone) btnClass = 'btn-store';
          }
        }

        const card = document.createElement('div');
        card.className = `mission-card${isDone?' completed':isProgress?' in-progress':''}${isStore?' store-mission':''}`;
        card.style.animationDelay = `${i * 0.08}s`;
        if (cardStyle) card.style = card.style.cssText + cardStyle;
        
        if (isQuiz) {
          card.innerHTML = `
            <div class="card-top">
              <div style="flex:1">
                <div class="mission-title"><span style="margin-right:8px">${m.emoji}</span>${m.area}</div>
                <div class="mission-topic">ÁREA DE LA CARRERA</div>
              </div>
              <div class="card-badges">
                <span class="status-badge ${statusClass}">${statusText}</span>
                <span class="diff-badge diff-media">MEDIA</span>
              </div>
            </div>
            <div class="mission-desc">Demuestra tus conocimientos y capacidad en esta área.</div>
            <div class="card-footer">
              <span class="pts-badge">+150 pts aprox.</span>
              <span class="time-badge">⏱ ${m.num_questions} preguntas</span>
            </div>
            <button class="${'btn-mission ' + btnClass}" onclick="${clickAction}" ${isDone && !isStore ? 'disabled' : ''}>${btnText}</button>
          `;
        } else {
          const meta = MISSION_META[m.mission_type] || { icon:'🛍️', diff:'ESPECIAL', diffClass:'diff-media', pts:'+150 pts', time:'Libre', desc:'Navega por la tienda real, agrega productos al carrito y completa el checkout.' };
          card.innerHTML = `
            <div class="card-top">
              <div style="flex:1">
                <div class="mission-title"><span style="margin-right:8px">${meta.icon}</span>${m.title || meta.title || 'La Tienda'}</div>
                <div class="mission-topic">${m.topic || meta.topic || 'CUSTOMER JOURNEY'}</div>
              </div>
              <div class="card-badges">
                <span class="status-badge ${statusClass}">${statusText}</span>
                <span class="diff-badge ${meta.diffClass}">${meta.diff}</span>
              </div>
            </div>
            <div class="mission-desc">${m.desc || meta.desc || meta.description || 'Explora la tienda real.'}</div>
            <div class="card-footer">
              <span class="pts-badge">${meta.pts}</span>
              <span class="time-badge">⏱ ${meta.time}</span>
            </div>
            <button class="${'btn-mission ' + btnClass}" onclick="${clickAction}" ${isDone && !isStore ? 'disabled' : ''}>${btnText}</button>
          `;
        }
        grid.appendChild(card);
      });
    }

    async function loadData() {
"""

text = re.sub(r'\s+async function loadData\(\) \{', '\n\n' + render_missions_patch, text, count=1)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Restored renderMissions and startMission in hub.html")

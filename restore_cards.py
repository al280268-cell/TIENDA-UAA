import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace renderMissions with proper CSS classes
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
        card.className = `mission-card${isDone?' completed':isProgress?' in-progress':''}${isStore?' store-mission':''}`;
        card.style.animationDelay = `${i * 0.08}s`;
        
        if (isQuiz) {
          // Render Career Area Card using original CSS classes
          card.innerHTML = `
            <div class="card-top">
              <div style="flex:1">
                <div class="mission-title">${m.emoji} ${m.area}</div>
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
            <button class="btn-mission ${btnClass}" onclick="window.location.href='mision.html?mission=${m.mission_id}'">${btnText}</button>
          `;
        } else {
          // Render Store Card (or fallback old cards) using original CSS classes
          const meta = MISSION_META[m.mission_type] || { icon:'🛒', diff:'ESPECIAL', diffClass:'diff-media', pts:'+150 pts', time:'Libre', desc: 'Resuelve el problema en la tienda.', topic: 'MISIÓN' };
          card.innerHTML = `
            <div class="card-top">
              <div style="flex:1">
                <div class="mission-title">${meta.icon} ${m.title || meta.title || 'La Tienda'}</div>
                <div class="mission-topic">${m.topic || meta.topic || 'CUSTOMER JOURNEY'}</div>
              </div>
              <div class="card-badges">
                <span class="status-badge ${statusClass}">${statusText}</span>
                <span class="diff-badge ${meta.diffClass}">${meta.diff}</span>
              </div>
            </div>
            <div class="mission-desc">${m.desc || meta.desc || 'Explora y resuelve los problemas del E-Commerce.'}</div>
            <div class="card-footer">
              <span class="pts-badge">${meta.pts}</span>
              <span class="time-badge">⏱ ${meta.time}</span>
            </div>
            <button class="btn-mission ${btnClass}" onclick="window.location.href='game.html?mission=${m.mission_id}'">${btnText}</button>
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
"""

text = re.sub(r'function renderMissions\(missions\)\s*\{.*?(?=async function startMission)', render_missions_patch.strip() + '\n\n    ', text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Card design restored!")

import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Modify renderMissions to be completely correct and safe
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
          // Render Career Area Card
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
          // Render Store Card (or fallback old cards)
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
      
      // Update progress bar
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

text = re.sub(r'function renderMissions\(missions\)\s*\{.*?(?=async function init\(\))', render_missions_patch.strip() + '\n\n    ', text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Hub.html fixed!")

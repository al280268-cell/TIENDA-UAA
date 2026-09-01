import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

old_fin = """    } else if (phase === 'finished') {
      if (_timerInterval) clearInterval(_timerInterval);
      // Save leaderboard to session for results.html
      if (state.players && state.players.length) {
        const sorted = [...state.players].sort((a,b) => (b.points||0) - (a.points||0));
        sessionStorage.setItem('uaa_game_results', JSON.stringify({ leaderboard: sorted }));
        const me = sorted.find(p => p.player_id === P.id);
        if (me) {
          sessionStorage.setItem('uaa_my_rank', String(me.rank || sorted.indexOf(me) + 1));
          sessionStorage.setItem('uaa_my_points', String(me.points || P.pts));
        }
      }
      // Redirect to the store simulation mission instead of jumping straight to results
      setTimeout(() => { window.location.href = 'store.html?mission=tienda_final'; }, 1500);
      showScreen('screen-podium');
      document.getElementById('podium').innerHTML = '<div style="text-align:center;font-size:2rem;padding:40px">\ud83d\uded2 Abriendo simulador de tienda\u2026</div>';
      document.getElementById('others-list').innerHTML = '';
      launchConfetti();
    }"""

new_fin = """    } else if (phase === 'finished') {
      if (_timerInterval) clearInterval(_timerInterval);
      // Save leaderboard to session for results.html
      if (state.players && state.players.length) {
        const sorted = [...state.players].sort((a,b) => (b.points||0) - (a.points||0));
        sessionStorage.setItem('uaa_game_results', JSON.stringify({ leaderboard: sorted }));
        const me = sorted.find(p => p.player_id === P.id);
        if (me) {
          sessionStorage.setItem('uaa_my_rank', String(me.rank || sorted.indexOf(me) + 1));
          sessionStorage.setItem('uaa_my_points', String(me.points || P.pts));
        }
      }
      showScreen('screen-podium');
      // Announce the transition to the final store simulation
      const podiumWrap = document.querySelector('.podium-wrap');
      podiumWrap.innerHTML = `
        <div style="text-align:center;padding:20px;animation:slideUp 0.6s ease">
          <div style="font-size:4rem;margin-bottom:10px">🏁</div>
          <div style="font-family:var(--bang);font-size:2.8rem;color:var(--gold);line-height:1;margin-bottom:15px;text-shadow:0 0 20px rgba(255,215,0,0.5);letter-spacing:1px">¡PREGUNTAS COMPLETADAS!</div>
          <div style="font-size:1.1rem;color:rgba(255,255,255,0.85);max-width:460px;margin:0 auto 30px;line-height:1.5">
            Has terminado todas las rondas de preguntas.<br><br>
            Para finalizar el reto y ganar tus <b>últimos 150 puntos</b>, 
            tendrás que vivir la experiencia real de compra en la tienda en línea.
          </div>
          <button onclick="window.location.href='store.html?mission=tienda_final'" style="background:var(--gold);color:#000;border:none;padding:16px 36px;font-family:var(--bang);font-size:1.5rem;border-radius:12px;cursor:pointer;box-shadow:0 10px 30px rgba(255,215,0,0.3);transition:transform 0.2s" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='none'">ENTRAR A LA TIENDA →</button>
          <div style="margin-top:20px;font-size:0.8rem;color:rgba(255,255,255,0.4)">Serás redirigido en unos segundos...</div>
        </div>
      `;
      setTimeout(() => { window.location.href = 'store.html?mission=tienda_final'; }, 10000);
      launchConfetti();
    }"""

text = text.replace(old_fin, new_fin)
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated hub.html")

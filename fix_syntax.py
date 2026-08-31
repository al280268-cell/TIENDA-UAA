import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix renderLeaderboard
lb_patch = r"""function renderLeaderboard(board) {
      const cont = document.getElementById('lb-chips');
      cont.innerHTML = '';
      board.forEach((p, i) => {
        const isMe = (p.id || p.player_id) === player.id;
        const rank = i + 1;
        const rankClass = rank===1?'gold':rank===2?'silver':rank===3?'bronze':'';
        const medal = rank===1?'🥇':rank===2?'🥈':rank===3?'🥉':'#'+rank;
        const color = p.color || p.avatar_color || '#333';
        const initials = p.initials || p.avatar_initials || '?';
        const chip = document.createElement('div');
        chip.className = `lb-chip${isMe?' me':''}`;
        chip.innerHTML = `
          <div class="lb-chip-avatar" style="background:${color}">${initials}</div>
          <span class="lb-chip-rank ${rankClass}">${medal}</span>
          <span class="lb-chip-name">${p.name}</span>
          <span class="lb-chip-pts">⭐ ${p.points}</span>`;
        cont.appendChild(chip);
      });
    }"""
text = re.sub(r'function renderLeaderboard\(board\) \{.*?</script>', lb_patch.strip() + '\n\n' + r"""
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
          if (qRes.ok && qRes.data && qRes.data.missions) {
            missions = qRes.data.missions.map(m => ({
              ...m,
              is_quiz: true
            }));
          }
        } catch(e) {}

        if(storeMission) missions.push(storeMission);

        const lRes = await api('GET', `/api/scoring/leaderboard/${player.code}`);
        let leaderboard = MOCK_LEADERBOARD;
        if (lRes.ok && Array.isArray(lRes.data) && lRes.data.length > 0) {
            leaderboard = lRes.data;
        }
        renderLeaderboard(leaderboard);

        const sRes = await api('GET', `/api/games/${player.code}/state`);
        if (sRes.ok && sRes.data && sRes.data.time_remaining !== undefined) {
          window._timeLeft = sRes.data.time_remaining;
          renderTimer();
          if (sRes.data.status === 'finished' || sRes.data.time_remaining <= 0) {
            goToResults();
          }
        }

        const me = leaderboard.find(p => (p.player_id || p.id) === player.id);
        if (me) {
          player.pts = me.points;
          sessionStorage.setItem('uaa_my_points', me.points);
          updateHUD();
        }
      }

      renderProgress(missions);
      renderMissions(missions);
    }

    async function init() {
      if (!player.code || !player.id) console.warn('Sin sesión — usando mock data');
      updateHUD();
      await loadData();
      setInterval(loadData, 5000);
      setInterval(() => {
        if (window._timeLeft > 0) {
          window._timeLeft--;
          renderTimer();
        }
      }, 1000);
    }

    init();
  </script>
""", text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed syntax error in hub.html")

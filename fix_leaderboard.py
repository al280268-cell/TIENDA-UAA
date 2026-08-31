import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix renderLeaderboard
lb_patch = r'''
    function renderLeaderboard(board) {
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
        chip.className = lb-chip;
        chip.innerHTML = 
          <div class="lb-chip-avatar" style="background:"></div>
          <span class="lb-chip-rank "></span>
          <span class="lb-chip-name"></span>
          <span class="lb-chip-pts">⭐ </span>;
        cont.appendChild(chip);
      });
    }
'''
text = re.sub(r'    function renderLeaderboard\(board\) \{.*?\n    \}', lb_patch.strip(), text, flags=re.DOTALL)

# Fix loadData leaderboard parsing
loadData_patch = r'''
      const lRes = await api('GET', /api/scoring/leaderboard/);
      let leaderboard = MOCK_LEADERBOARD;
      if (lRes.ok && Array.isArray(lRes.data) && lRes.data.length > 0) {
          leaderboard = lRes.data;
      }
      renderLeaderboard(leaderboard);

      const sRes = await api('GET', /api/games//state);
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
'''
text = re.sub(r'      const lRes = await api\(\'GET\', /api/scoring/leaderboard/\$\{player\.code\}\).*?updateHUD\(\);\n      \}', loadData_patch.strip(), text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed leaderboard mapping in hub.html")

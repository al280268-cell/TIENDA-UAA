with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find and replace the full updateActiveGamePanel function
start_marker = "    function updateActiveGamePanel(games) {"
end_marker = "\n    async function loadGames("

si = text.find(start_marker)
ei = text.find(end_marker, si)

if si == -1 or ei == -1:
    print(f"Markers not found: si={si} ei={ei}")
    exit(1)

old_func = text[si:ei]
print("Old function length:", len(old_func))

new_func = """    function updateActiveGamePanel(games) {
      // Find most recent waiting/active game
      const activeOrWaiting = games.find(g => g.status === 'waiting' || g.status === 'active');
      const statusEl = document.getElementById('dash-active-status');
      const codeInp  = document.getElementById('live-code');

      if (activeOrWaiting) {
        const gc = activeOrWaiting.code || activeOrWaiting.game_code || '';
        Admin.activeGame = { game_code: gc, status: activeOrWaiting.status };

        // Auto-fill the code field if empty
        if (codeInp && !codeInp.value) codeInp.value = gc;

        // Update status badge
        if (statusEl) {
          const color = activeOrWaiting.status === 'active' ? '#00E676' : '#F59E0B';
          statusEl.innerHTML = `Partida activa: <strong style="color:${color};font-size:1.1em">${gc}</strong>
            <span style="font-size:.75rem;color:rgba(255,255,255,.5);margin-left:8px">[${activeOrWaiting.status.toUpperCase()}]</span>`;
        }

        // If game is active and live panel not showing, auto-connect
        if (activeOrWaiting.status === 'active' && _liveCode === gc) {
          if (!_liveInterval) _connectLivePolling();
        }
      } else {
        if (statusEl) statusEl.innerHTML = '<span style="color:rgba(255,255,255,.35)">Sin partida activa</span>';
      }
    }
"""

text = text[:si] + new_func + text[ei:]

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("updateActiveGamePanel replaced OK, new len:", len(text))

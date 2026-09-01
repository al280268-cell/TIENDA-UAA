with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

old_poll_bad = """async function poll() {
  if (!P.code) return;
  const state = await api('GET', `/api/games/${P.code}/state`);
  if (!state) return;

  // Update player points from leaderboard
  const me = (state.players || []).find(p => p.player_id === P.id);
  if (me) {
    if (me.points > P.pts) { P.pts = me.points; sessionStorage.setItem('uaa_my_points', P.pts); }
    if (me.rank) { P.rank = me.rank; sessionStorage.setItem('uaa_my_rank', me.rank); }
    updateHUD(phase);
  }

  const phase = (state.status === 'finished' && state.mission_phase === 'lobby')
    ? 'finished'
    : (state.mission_phase || 'lobby');"""

new_poll_fixed = """async function poll() {
  if (!P.code) return;
  const state = await api('GET', `/api/games/${P.code}/state`);
  if (!state) return;

  // Determine phase FIRST (before any use of it)
  const phase = (state.status === 'finished' && state.mission_phase === 'lobby')
    ? 'finished'
    : (state.mission_phase || 'lobby');

  // Update player points from leaderboard
  const me = (state.players || []).find(p => p.player_id === P.id);
  if (me) {
    if (me.points > P.pts) { P.pts = me.points; sessionStorage.setItem('uaa_my_points', P.pts); }
    if (me.rank) { P.rank = me.rank; sessionStorage.setItem('uaa_my_rank', me.rank); }
    updateHUD(phase);
  }"""

if old_poll_bad in text:
    text = text.replace(old_poll_bad, new_poll_fixed)
    print("Fixed poll() TDZ bug OK")
else:
    import re
    # Try to find it with flexible whitespace
    idx = text.find("async function poll()")
    safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:idx+600])
    print("Could not match exactly. Current:")
    print(repr(safe))

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "w", encoding="utf-8") as f:
    f.write(text)

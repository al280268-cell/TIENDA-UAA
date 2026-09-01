with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find and replace liveLaunch completely
idx_ll = text.find('    async function liveLaunch()')
idx_lc = text.find('\n    async function liveConnect()', idx_ll)

if idx_ll == -1 or idx_lc == -1:
    print(f'ERROR markers: ll={idx_ll} lc={idx_lc}')
    exit(1)

# Simple, robust liveLaunch - no fancy stuff
new_fn = '''    async function liveLaunch() {
      const statusEl = document.getElementById('live-status-msg');
      const btnLaunch = document.getElementById('btn-launch');
      const btnStart  = document.getElementById('btn-start-questions');

      if (btnLaunch) btnLaunch.textContent = 'Creando...';
      if (statusEl)  statusEl.textContent  = 'Creando sala de juego...';

      // Stop background polling to avoid DB conflicts
      if (_liveInterval) { clearInterval(_liveInterval); _liveInterval = null; }

      const maxPl = parseInt(document.getElementById('dash-max-players')?.value) || 30;
      _liveDuration = parseInt(document.getElementById('live-duration')?.value) || 30;

      try {
        const r1 = await fetch('/api/games/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: 'Feria UAA', max_players: maxPl })
        });
        const d1 = await r1.json();

        if (!r1.ok || !d1.game_code) {
          if (statusEl) statusEl.innerHTML = '<span style="color:#E62429">Error: ' + (d1.detail || 'sin respuesta') + '</span>';
          if (btnLaunch) btnLaunch.textContent = 'CREAR NUEVA PARTIDA (LOBBY)';
          return;
        }

        _liveCode = d1.game_code;
        if (statusEl) statusEl.innerHTML = 'Sala lista: <strong style="color:#FFD700;font-size:1.3em">' + _liveCode + '</strong> &mdash; jugadores entran con ese codigo en la pagina principal';
        if (btnLaunch) btnLaunch.textContent = 'CREAR NUEVA PARTIDA (LOBBY)';

        // Show the ARRANCAR button and live panel
        if (btnStart) { btnStart.style.display = 'inline-block'; btnStart.disabled = false; btnStart.textContent = 'ARRANCAR PREGUNTAS'; }
        const lp = document.getElementById('live-panel');
        if (lp) lp.style.display = 'block';

        // Start watching players every 3s
        _liveInterval = setInterval(livePoll, 3000);
        livePoll();

      } catch(e) {
        if (statusEl) statusEl.innerHTML = '<span style="color:#E62429">Error de conexion: ' + e.message + '</span>';
        if (btnLaunch) btnLaunch.textContent = 'CREAR NUEVA PARTIDA (LOBBY)';
      }
    }

    async function startQuestions() {
      if (!_liveCode) { alert('Primero crea una sala'); return; }
      const dur = parseInt(document.getElementById('live-duration')?.value) || 30;
      const res = parseInt(document.getElementById('live-results-sec')?.value) || 5;
      const btn = document.getElementById('btn-start-questions');
      const tok = sessionStorage.getItem('uaa_admin_token') || '';
      if (btn) { btn.disabled = true; btn.textContent = 'Arrancando...'; }

      try {
        const r = await fetch('/api/games/' + _liveCode + '/launch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok },
          body: JSON.stringify({ duration_sec: dur, results_sec: res })
        });
        const d = await r.json();
        if (!r.ok) {
          if (btn) { btn.disabled = false; btn.textContent = 'ARRANCAR PREGUNTAS'; }
          const el = document.getElementById('live-status-msg');
          if (el) el.innerHTML = '<span style="color:#E62429">Error: ' + (d.detail || 'fallo') + '</span>';
          return;
        }
        if (btn) btn.style.display = 'none';
        const el = document.getElementById('live-status-msg');
        if (el) el.textContent = 'Juego corriendo: ' + _liveCode + ' - ' + (d.total_missions||6) + ' misiones x ' + dur + 's automaticas';
      } catch(e) {
        if (btn) { btn.disabled = false; btn.textContent = 'ARRANCAR PREGUNTAS'; }
      }
    }

'''

text = text[:idx_ll] + new_fn + text[idx_lc:]

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('OK len:', len(text))

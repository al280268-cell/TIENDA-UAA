
const S = {
  code:  sessionStorage.getItem('uaa_game_code') || sessionStorage.getItem('uaa_gameCode') || '',
  pid:   sessionStorage.getItem('uaa_player_id') || '',
  token: sessionStorage.getItem('uaa_player_token') || '',
  name:  sessionStorage.getItem('uaa_player_name') || 'Jugador',
  pts:   parseInt(sessionStorage.getItem('uaa_my_points') || '0', 10),
  streak: 0,
  mission: null, questions: [], qi: 0, gained: 0, correctCount: 0, qStart: 0,
};

document.getElementById('nameChip').textContent = S.name;
setPts(S.pts);

async function api(method, url, body){
  const opts = { method, headers:{'Content-Type':'application/json'} };
  if (S.token) opts.headers['Authorization'] = 'Bearer ' + S.token;
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  return res.json();
}

// ── PUNTOS — siempre guarda en sessionStorage ────────────────────────────
function setPts(v){
  S.pts = Math.max(0, v);
  document.getElementById('ptsChip').textContent = '⭐ ' + S.pts;
  sessionStorage.setItem('uaa_my_points', S.pts);   // ← FIX: persiste siempre
}

// ── TIMER ─────────────────────────────────────────────────────────────────
let matchEnded = false;
async function initTimer(){
  const chip = document.getElementById('timeChip');
  if(!S.code){ chip.style.display='none'; return; }

  // Try sessionStorage first for a reliable local countdown
  let endTs = parseInt(sessionStorage.getItem('uaa_match_end') || '0');
  try {
    const st = await api('GET', `/api/games/${S.code}/state`);
    const remaining = (st && typeof st.time_remaining === 'number' && st.time_remaining >= 0)
                      ? st.time_remaining
                      : (st && st.duration_seconds) || 240;
    if (!endTs || endTs < Date.now()) {
      endTs = Date.now() + remaining * 1000;
      sessionStorage.setItem('uaa_match_end', String(endTs));
    }
    if (st && (st.status === 'finished' || st.time_remaining === 0)) { endMatch(); return; }
  } catch(e) {
    if (!endTs || endTs < Date.now()) endTs = Date.now() + 240000;
  }

  function tick(){
    const left = Math.max(0, Math.round((endTs - Date.now())/1000));
    const mm = String(Math.floor(left/60)).padStart(2,'0');
    const ss = String(left%60).padStart(2,'0');
    chip.textContent = '⏱ ' + mm + ':' + ss;
    chip.className = 'chip time';
    if (left <= 30) chip.classList.add('crit');
    else if (left <= 60) chip.classList.add('warn');
    if (left <= 0 && !matchEnded) endMatch();
  }
  tick();
  setInterval(tick, 1000);
}

function endMatch(){
  matchEnded = true;
  document.getElementById('overEnd').classList.add('show');
  setTimeout(()=>{ window.location.href = 'results.html'; }, 2600);
}

// ── LISTA ─────────────────────────────────────────────────────────────────
async function loadList(){
  const grid = document.getElementById('mGrid');
  if(!S.code || !S.pid){
    grid.innerHTML = '<div style="color:var(--muted)">No hay sesión de partida. Únete primero desde la página de inicio.</div>';
    return;
  }
  let data;
  try { data = await api('GET', `/api/quiz/missions/${S.code}/${S.pid}`); }
  catch(e){ grid.innerHTML = '<div style="color:var(--sp-red)">Error cargando misiones.</div>'; return; }
  grid.innerHTML = '';
  (data.missions||[]).forEach(m=>{
    const done = m.status === 'completed';
    const el = document.createElement('div');
    el.className = 'm-card' + (done?' done':'');
    el.innerHTML = `
      <span class="badge ${done?'dn':'av'}">${done?'✓ LISTA':'JUGAR'}</span>
      <div class="emo">${m.emoji}</div>
      <div class="area">${m.area}</div>
      <div class="meta">${m.num_questions} preguntas</div>`;
    if(!done) el.onclick = ()=> location.href = `mision.html?mission=${m.mission_id}`;
    grid.appendChild(el);
  });
}

// ── JUEGO ─────────────────────────────────────────────────────────────────
async function startMission(mid){
  document.getElementById('listView').classList.add('hidden');
  document.getElementById('playView').classList.remove('hidden');
  let data;
  try { data = await api('POST', '/api/quiz/start', {player_id:S.pid, game_code:S.code, mission_id:mid}); }
  catch(e){ document.getElementById('qText').textContent = 'Error iniciando la misión.'; return; }
  if(!data || !data.questions){ document.getElementById('qText').textContent = 'No se pudo cargar la misión.'; return; }
  S.mission = data; S.questions = data.questions; S.qi = 0; S.gained = 0; S.correctCount = 0;
  document.getElementById('qArea').textContent = (data.emoji||'') + '  ' + data.area;
  renderQuestion();
}

function renderQuestion(){
  const q = S.questions[S.qi];
  S.qStart = Date.now();
  document.getElementById('pbar').style.width = (S.qi/S.questions.length*100) + '%';
  const diffClass = 'd-' + (q.difficulty||'media');
  document.getElementById('qText').innerHTML =
    `${q.text}<span class="q-diff ${diffClass}">${(q.difficulty||'media').toUpperCase()} · ${q.points} pts</span>`;
  const opts = document.getElementById('opts'); opts.innerHTML = '';
  q.options.forEach((txt, idx)=>{
    const b = document.createElement('button');
    b.className = 'opt'; b.textContent = txt;
    b.onclick = ()=> choose(idx, b);
    opts.appendChild(b);
  });
  const fb = document.getElementById('fb'); fb.className='fb';
  document.getElementById('nextBtn').classList.add('hidden');
}

async function choose(idx, btn){
  if (matchEnded) return;
  const q = S.questions[S.qi];
  document.querySelectorAll('#opts .opt').forEach(b=> b.disabled=true);
  const took = Date.now() - S.qStart;
  let r;
  try {
    r = await api('POST', '/api/quiz/answer', {
      player_id:S.pid, game_code:S.code, mission_id:S.mission.mission_id,
      question_id:q.id, answer_index:idx, time_taken_ms:took, streak:S.streak
    });
  } catch(e){ r = {correct:false, net:0, explanation:'', correct_index:-1}; }

  const btns = document.querySelectorAll('#opts .opt');
  if (r.correct) { btn.classList.add('correct'); S.streak++; S.correctCount++; }
  else {
    btn.classList.add('wrong'); S.streak = 0;
    if (r.correct_index >= 0 && btns[r.correct_index]) btns[r.correct_index].classList.add('correct');
  }
  S.gained += (r.net||0);

  // ── Sync points — use server total if available, else accumulate locally
  if (typeof r.total_points === 'number') setPts(r.total_points);
  else setPts(S.pts + (r.net||0));

  const fb = document.getElementById('fb');
  fb.className = 'fb show ' + (r.correct ? 'ok' : 'no');
  document.getElementById('fbV').textContent = r.correct
    ? `¡Correcto! +${r.net} pts` + (r.speed_bonus?`  ⚡+${r.speed_bonus}`:'') + (r.streak_bonus?`  🔥+${r.streak_bonus}`:'')
    : `Incorrecto  ${r.net} pts`;
  document.getElementById('fbE').textContent = r.explanation || '';

  const nb = document.getElementById('nextBtn');
  nb.classList.remove('hidden');
  nb.textContent = (S.qi+1 >= S.questions.length) ? 'Terminar misión →' : 'Siguiente →';
  nb.onclick = next;
}

function next(){
  S.qi++;
  if (S.qi >= S.questions.length) return finish();
  renderQuestion();
}

function finish(){
  document.getElementById('pbar').style.width = '100%';
  document.getElementById('playView').classList.add('hidden');
  const dv = document.getElementById('doneView'); dv.classList.remove('hidden');
  document.getElementById('doneArea').textContent = (S.mission.emoji||'') + ' ' + S.mission.area;
  document.getElementById('doneScore').textContent = (S.gained>=0?'+':'') + S.gained + ' pts';
  document.getElementById('doneDetail').textContent =
    `${S.correctCount} de ${S.questions.length} correctas · Puntaje total: ${S.pts} ⭐`;
}

// ── ARRANQUE ──────────────────────────────────────────────────────────────
initTimer();
const mid = new URLSearchParams(location.search).get('mission');
if (mid) startMission(mid); else loadList();

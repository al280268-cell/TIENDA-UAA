import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\game.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace renderMission start and remove old speed_search block, replace with renderSubQuestion logic
render_logic = r"""
    function renderMission(type, data) {
      if (data.is_multi) {
        window.multiData = data;
        window.multiType = type;
        window.currentMultiIndex = 0;
        window.multiAnswers = [];
        renderSubQuestion();
        
        const barTime = MISSION_TIMES[type] || 45;
        startTimerBar(barTime);
        return;
      }
      
      let html = '';
"""

text = re.sub(r'    function renderMission\(type, data\) \{\s*let html = \'\';', render_logic.strip('\n'), text)

sub_q_func = r"""
    function renderSubQuestion() {
      const q = window.multiData.questions[window.currentMultiIndex];
      const type = window.multiType;
      const totalQs = window.multiData.questions.length;
      
      let html = `<div style="font-size:0.8rem; color:var(--uaa-red); font-weight:700; margin-bottom:12px; text-transform:uppercase;">PREGUNTA ${window.currentMultiIndex + 1} DE ${totalQs}</div>`;
      
      if(type === 'ecom_decision' || type === 'checkout_debug' || type === 'speed_search') {
        const intro = q.scenario || q.context || 'Lee cuidadosamente la siguiente situación y elige la mejor opción.';
        html += `<div class="intro-card"><p>${intro}</p></div>`;
        html += `<div class="question">${q.question || '¿Qué deberías hacer?'}</div><div id="opts">`;
        (q.options || []).forEach((opt, i) => {
          html += `<button class="btn-option" onclick="selectOption('${opt.id || i}', this)">${opt.text}</button>`;
        });
        html += `</div>`;
      } else if(type === 'fraud_detect') {
        const listings = q.listings || q.products || [];
        html += `<div class="intro-card"><p>${q.scenario || q.intro || 'Un comprador reportó estas tiendas. Analiza los listados y encuentra cuál tiene señales de fraude.'}</p></div>`;
        html += `<div class="question">${q.question || '¿Cuál es el listado sospechoso?'}</div>`;
        listings.forEach((p, i) => {
          const meta = [];
          if(p.rating) meta.push('⭐ ' + p.rating);
          if(p.sales_count) meta.push('📦 ' + p.sales_count + ' ventas');
          if(p.delivery_time) meta.push('🚚 ' + p.delivery_time);
          if(p.trust_badge) meta.push('✔️ ' + p.trust_badge);
          html += `<div class="btn-option" style="text-align:left;" onclick="selectOption('${p.id || i}', this)">
            <div style="font-weight:700;margin-bottom:4px;">${p.emoji ? p.emoji + ' ' : ''}${p.name}</div>
            <div style="color:var(--red);font-weight:600;margin-bottom:6px;">${p.price || ''}</div>
            <div style="font-size:0.8rem;color:var(--muted);line-height:1.6;">${meta.join('<br>')}</div>
          </div>`;
        });
      }
      
      DOM.container.innerHTML = html;
      window.answered = false;
    }
"""

text = text.replace('    function startTimerBar(seconds) {', sub_q_func + '\n    function startTimerBar(seconds) {')

submit_logic = r"""
    async function submitAnswer(answer) {
      if(answered) return;
      
      if (window.multiData) {
        window.multiAnswers.push(answer);
        if (window.currentMultiIndex < window.multiData.questions.length - 1) {
          window.currentMultiIndex++;
          renderSubQuestion();
          return;
        }
        answer = window.multiAnswers;
      }
      
      answered = true;
"""

text = re.sub(r'    async function submitAnswer\(answer\) \{\s*if\(answered\) return;\s*answered = true;', submit_logic.strip('\n'), text)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\game.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS JS INJECTED")

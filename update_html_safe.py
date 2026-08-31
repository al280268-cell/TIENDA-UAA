import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\game.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace renderMission start
render_patch = '''
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
'''
text = text.replace("    function renderMission(type, data) {\n      let html = '';", render_patch.strip('\n'))

# Add renderSubQuestion
sub_q_func = '''
    function renderSubQuestion() {
      const q = window.multiData.questions[window.currentMultiIndex];
      const type = window.multiType;
      const totalQs = window.multiData.questions.length;
      const progressHtml = <div style="font-size:0.8rem; color:var(--uaa-red); font-weight:700; margin-bottom:12px;">PREGUNTA  DE </div>;
      
      let html = progressHtml;
      
      if(type === 'ecom_decision' || type === 'checkout_debug' || type === 'speed_search') {
        const intro = q.scenario || q.context || 'Lee cuidadosamente la siguiente situación y elige la mejor opción.';
        html += <div class="intro-card"><p></p></div>;
        html += <div class="question"></div><div id="opts">;
        (q.options || []).forEach((opt, i) => {
          html += <button class="btn-option" onclick="selectOption('', this)"></button>;
        });
        html += </div>;
      } else if(type === 'fraud_detect') {
        const listings = q.listings || q.products || [];
        html += <div class="intro-card"><p></p></div>;
        html += <div class="question"></div>;
        listings.forEach((p, i) => {
          const meta = [];
          if(p.rating) meta.push('⭐ ' + p.rating);
          if(p.sales_count) meta.push('📦 ' + p.sales_count + ' ventas');
          if(p.delivery_time) meta.push('🚚 ' + p.delivery_time);
          if(p.trust_badge) meta.push('✔️ ' + p.trust_badge);
          html += <div class="btn-option" style="text-align:left;" onclick="selectOption('', this)">
            <div style="font-weight:700;margin-bottom:4px;"></div>
            <div style="color:var(--red);font-weight:600;margin-bottom:6px;"></div>
            <div style="font-size:0.8rem;color:var(--muted);line-height:1.6;"></div>
          </div>;
        });
      }
      
      DOM.container.innerHTML = html;
      window.answered = false; // allow answering the next question
    }
'''
text = text.replace('    function startTimerBar(seconds) {', sub_q_func + '\n    function startTimerBar(seconds) {')

# Modify submitAnswer
submit_patch = '''
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
'''
text = text.replace('    async function submitAnswer(answer) {\n      if(answered) return;\n      answered = true;', submit_patch.strip('\n'))

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\game.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("HTML PATCHED")

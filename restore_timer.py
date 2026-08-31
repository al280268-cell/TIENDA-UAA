import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

missing_functions = r"""
    let _redirecting = false;
    
    function goToResults() {
      if (_redirecting) return;
      _redirecting = true;
      window.location.href = 'results.html';
    }

    function renderTimer() {
      const t = Math.max(0, window._timeLeft ?? 0);
      const el = document.getElementById('nav-timer');
      if (!el) return;
      const mm = Math.floor(t/60).toString().padStart(2,'0');
      const ss = (t%60).toString().padStart(2,'0');
      el.textContent = `${mm}:${ss}`;
      el.classList.toggle('warn', t <= 60);
      el.style.color = t <= 30 ? '#E62429' : (t <= 60 ? '#F59E0B' : '');
    }

    async function loadData() {
"""

text = re.sub(r'\s+async function loadData\(\) \{', '\n' + missing_functions, text, count=1)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Restored renderTimer and goToResults")

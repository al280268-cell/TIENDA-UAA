import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Add a back button inside playView
back_btn_patch = r'''
  <div id="playView" class="hidden">
    <div style="margin-bottom: 15px; text-align: left;">
      <button onclick="window.location.href='hub.html'" class="btn sec" style="padding: 6px 12px; font-size: 12px; border: 1px solid var(--border); background: var(--bg); color: var(--text); border-radius: 6px; cursor: pointer;">← Volver al mapa</button>
    </div>
    <div class="q-area" id="qArea">ÁREA</div>
'''

text = text.replace('<div id="playView" class="hidden">\n    <div class="q-area" id="qArea">REA</div>', back_btn_patch.strip())
text = text.replace('<div id="playView" class="hidden">\n    <div class="q-area" id="qArea">ÁREA</div>', back_btn_patch.strip())

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Added back button to mision.html")

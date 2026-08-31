import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the messy button with a clean one
old_btn = r'''<div style="margin-bottom: 15px; text-align: left;">
      <button onclick="window.location.href='hub.html'" class="btn sec" style="padding: 6px 12px; font-size: 12px; border: 1px solid var(--border); background: var(--bg); color: var(--text); border-radius: 6px; cursor: pointer;">← Volver al mapa</button>
    </div>'''

new_btn = r'''<div style="margin-bottom: 15px; text-align: left;">
      <button onclick="window.location.href='hub.html'" class="btn sec">← Volver al mapa</button>
    </div>'''

text = text.replace(old_btn, new_btn)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'w', encoding='utf-8') as f:
    f.write(text)

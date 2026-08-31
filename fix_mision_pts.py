import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "function setPts(v){ S.pts = Math.max(0, v); document.getElementById('ptsChip').textContent = '⭐ ' + S.pts; }",
    "function setPts(v){ S.pts = Math.max(0, v); document.getElementById('ptsChip').textContent = '⭐ ' + S.pts; sessionStorage.setItem('uaa_my_points', S.pts); }"
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed setPts in mision.html to save to sessionStorage")

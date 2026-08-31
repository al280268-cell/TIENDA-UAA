import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Insert setPts(S.pts); after setting nameChip
text = text.replace("document.getElementById('nameChip').textContent = S.name;", "document.getElementById('nameChip').textContent = S.name;\nsetPts(S.pts);")

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed initialization in mision.html")

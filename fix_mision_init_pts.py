import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix initial points in S
text = text.replace("pts: 0, streak: 0,", "pts: parseInt(sessionStorage.getItem('uaa_my_points') || '0', 10), streak: 0,")

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\mision.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed S.pts initialization in mision.html")

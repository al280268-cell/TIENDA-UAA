import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('if (qRes && qRes.missions) {', 'if (qRes.ok && qRes.data && qRes.data.missions) {')
text = text.replace('missions = qRes.missions.map', 'missions = qRes.data.missions.map')

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html', 'r', encoding='utf-8') as f:
    admin_text = f.read()

admin_text = admin_text.replace('duration_seconds: 180,', 'duration_seconds: 240,')

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_text)

print("Fixes applied.")

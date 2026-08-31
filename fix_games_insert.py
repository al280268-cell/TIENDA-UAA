import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the insertion of rewards in games.py
text = re.sub(
    r'for p in prizes:\s*await db\.execute\(\s*"""INSERT INTO rewards.*?game_code\)\s*\)\s*await db\.commit\(\)',
    'await db.commit()',
    text,
    flags=re.DOTALL
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py', 'w', encoding='utf-8') as f:
    f.write(text)

import sqlite3
conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("DELETE FROM rewards WHERE id NOT IN ('cilindro', 'pelota', 'gallo', 'stickers')")
conn.commit()
conn.close()

print("Patched games.py and deleted duplicate rewards from DB")

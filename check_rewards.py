import sqlite3

conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("SELECT id, name FROM rewards")
rows = c.fetchall()
for r in rows:
    print(r)

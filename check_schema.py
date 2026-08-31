import sqlite3

conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("PRAGMA table_info(players)")
rows = c.fetchall()
print(rows)

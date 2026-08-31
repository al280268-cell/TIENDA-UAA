import sqlite3

conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("SELECT mission_type FROM player_missions WHERE game_code='UAA-2BR3'")
rows = c.fetchall()
print([r[0] for r in rows])

import sqlite3

conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("SELECT game_code, player_id, count(*) FROM player_missions GROUP BY game_code, player_id")
rows = c.fetchall()
print(rows)

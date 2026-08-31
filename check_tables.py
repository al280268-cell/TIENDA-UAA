import sqlite3
import json

conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("PRAGMA table_info(quiz_progress)")
print("quiz_progress:", c.fetchall())

c.execute("PRAGMA table_info(player_missions)")
print("player_missions:", c.fetchall())

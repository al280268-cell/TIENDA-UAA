import sqlite3
import json

conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
cursor = conn.cursor()
cursor.execute("SELECT mission_data FROM player_missions WHERE mission_type = 'checkout_debug' ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
if row:
    print(row[0])

import sqlite3

conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()

# Delete all existing rewards
c.execute("DELETE FROM rewards")

# Insert the 4 official rewards
rewards = [
    ('cilindro', 'Cilindro UAA', '🥤', 50, 50, 0, None, None, 0, 'Cilindro deportivo oficial de la UAA.'),
    ('pelota', 'Pelota UAA', '⚽', 50, 50, 0, None, None, 0, 'Pelota deportiva con escudo de la UAA.'),
    ('gallo', 'Llavero de Gallo', '🐓', 100, 100, 0, None, None, 0, 'Llavero metálico de la mascota oficial.'),
    ('stickers', 'Stickers Universitarios', '✨', 150, 150, 0, None, None, 0, 'Paquete de stickers para decorar.')
]

for r in rewards:
    c.execute(
        "INSERT INTO rewards (id, name, emoji, stock_initial, stock_remaining, min_points, min_rank, game_code, disabled, description) VALUES (?,?,?,?,?,?,?,?,?,?)",
        r
    )

conn.commit()
conn.close()
print("Rewards inventory wiped and replaced with the 4 official items.")

import asyncio
from httpx import AsyncClient
from backend.app import app
from fastapi.testclient import TestClient
import sqlite3

# find a valid checkout_debug mission
conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("SELECT id, player_id, game_code FROM player_missions WHERE mission_type='checkout_debug' LIMIT 1")
row = c.fetchone()

if row:
    client = TestClient(app)
    try:
        req = {"player_id": row[1], "game_code": row[2], "mission_id": row[0]}
        res = client.post("/api/missions/start", json=req)
        print("Start status:", res.status_code)
        print("Start body:", res.text)
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("No checkout_debug found in DB")

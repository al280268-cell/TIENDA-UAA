import asyncio
import sqlite3
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

print("Fetching players from DB to get Daf's player_id...")
conn = sqlite3.connect(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\game.db')
c = conn.cursor()
c.execute("SELECT id FROM players WHERE name='Daf' ORDER BY joined_at DESC LIMIT 1")
row = c.fetchone()
if row:
    pid = row[0]
    print(f"Daf player_id: {pid}")
    
    print("\nTesting Quiz API for Daf:")
    res_q = client.get(f"/api/quiz/missions/UAA-NY4L/{pid}")
    print("Quiz Status:", res_q.status_code)
    if res_q.status_code == 200:
        data = res_q.json()
        print("Quiz Missions Count:", len(data.get("missions", [])))
        print(data.get("missions", [])[:1]) # Print just first one to see what it looks like

    print("\nTesting Pool API for Daf:")
    res_p = client.get(f"/api/missions/pool/UAA-NY4L/{pid}")
    print("Pool Status:", res_p.status_code)
    if res_p.status_code == 200:
        data = res_p.json()
        print("Pool Missions Count:", len(data.get("missions", [])))
else:
    print("Could not find Daf in DB")


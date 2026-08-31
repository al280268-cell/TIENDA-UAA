import httpx
import json

# Fetch a pool for a fake player
res = httpx.get("http://localhost:8000/api/missions/pool/TESTCODE/TESTPLAYER")
data = res.json()
missions = data.get('missions', [])
print("Missions generated:", len(missions))

# Find checkout_debug
checkout_mission = next((m for m in missions if m['mission_type'] == 'checkout_debug'), None)
if checkout_mission:
    print("Found checkout_debug:", checkout_mission['mission_id'])
    
    # Start it
    start_req = {
        "player_id": "TESTPLAYER",
        "game_code": "TESTCODE",
        "mission_id": checkout_mission["mission_id"]
    }
    start_res = httpx.post("http://localhost:8000/api/missions/start", json=start_req)
    print("Start response status:", start_res.status_code)
    print("Start response data:", start_res.json())
else:
    print("No checkout_debug found!")

import httpx
import json

base = "http://localhost:8000"
# Create game
res = httpx.post(base + "/api/games/create", json={"game_code": "TESTNEW", "difficulty": "media"})
print("Create:", res.text)

# Join game
res = httpx.post(base + "/api/players/join", json={"player_name": "TestPlayer", "game_code": "TESTNEW"})
player_id = res.json()["player_id"]
print("Join:", player_id)

# Get pool
res = httpx.get(f"{base}/api/missions/pool/TESTNEW/{player_id}")
pool = res.json()
print("Pool size:", len(pool.get("missions", [])))

# Start one mission
for m in pool.get("missions", []):
    if m["mission_type"] == "checkout_debug":
        print("Starting checkout_debug", m["mission_id"])
        res = httpx.post(base + "/api/missions/start", json={"player_id": player_id, "game_code": "TESTNEW", "mission_id": m["mission_id"]})
        mdata = res.json().get("mission_data", {})
        print("IS_MULTI:", mdata.get("is_multi"))
        print("QUESTIONS:", len(mdata.get("questions", [])))
        if mdata.get("questions"):
            print("Q1 has options:", "options" in mdata["questions"][0])
        break

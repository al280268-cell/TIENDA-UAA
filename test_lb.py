import asyncio
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
print("Leaderboard UAA-CSLF:")
res = client.get("/api/scoring/leaderboard/UAA-CSLF")
print(res.status_code, res.text)

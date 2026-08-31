import asyncio
from httpx import AsyncClient
from backend.app import app
from fastapi.testclient import TestClient

client = TestClient(app)
try:
    res = client.get("/api/missions/pool/TESTCODE3/TESTPLAYER3")
    print(res.status_code)
    print(res.text)
except Exception as e:
    import traceback
    traceback.print_exc()

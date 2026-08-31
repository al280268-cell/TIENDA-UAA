import asyncio
from httpx import AsyncClient
from backend.app import app
from fastapi.testclient import TestClient

client = TestClient(app)
try:
    print("Testing Quiz API:")
    res_q = client.get("/api/quiz/missions/TESTCODE/TESTPLAYER")
    print(res_q.status_code)
    print(res_q.text[:200])

    print("\nTesting Pool API:")
    res_p = client.get("/api/missions/pool/TESTCODE/TESTPLAYER")
    print(res_p.status_code)
    print(res_p.text[:200])
except Exception as e:
    import traceback
    traceback.print_exc()

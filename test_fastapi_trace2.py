import asyncio
from httpx import AsyncClient
from backend.app import app
from fastapi.testclient import TestClient

client = TestClient(app)
try:
    res = client.get("/api/missions/pool/UAA-2BR3/a37b13e9-74d6-44ec-b9a6-c87568169123")
    print(res.status_code)
    print(res.text.encode('utf-8'))
except Exception as e:
    import traceback
    traceback.print_exc()

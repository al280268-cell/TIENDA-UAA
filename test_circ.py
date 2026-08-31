import asyncio
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
try:
    from backend.app import publish_to_ably
    print("SUCCESS")
except Exception as e:
    print("FAIL:", e)

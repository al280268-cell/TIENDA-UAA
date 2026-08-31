from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
print("Testing Quiz API:")
res_q = client.get("/api/quiz/missions/TESTCODE/TESTPLAYER")
print("Quiz Status:", res_q.status_code)
if res_q.status_code == 200:
    data = res_q.json()
    print("Quiz Missions Count:", len(data.get("missions", [])))

print("\nTesting Pool API:")
res_p = client.get("/api/missions/pool/TESTCODE/TESTPLAYER")
print("Pool Status:", res_p.status_code)
if res_p.status_code == 200:
    data = res_p.json()
    print("Pool Missions Count:", len(data.get("missions", [])))

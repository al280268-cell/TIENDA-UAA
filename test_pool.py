import httpx
res = httpx.get("http://localhost:8000/api/missions/pool/UAA-2BR3/a37b13e9-74d6-44ec-b9a6-c87568169123")
print(res.status_code)
print(res.text)

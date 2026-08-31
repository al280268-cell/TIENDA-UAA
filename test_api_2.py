import httpx

res = httpx.get("http://localhost:8000/api/missions/pool/TESTCODE2/TESTPLAYER2")
print("Status:", res.status_code)
print("Text:", res.text)

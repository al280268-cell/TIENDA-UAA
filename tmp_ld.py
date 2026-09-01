import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the full loadDashboard JS function
idx = text.find("async function loadDashboard()")
end = text.find("\n    async function loadGames()", idx)
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:end])
print(safe[:3000])

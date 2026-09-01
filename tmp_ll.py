with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the liveLaunch function
idx = text.find("async function liveLaunch()")
end = text.find("\n    async function liveConnect()", idx)
import re
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx:end])
print(safe[:2000])

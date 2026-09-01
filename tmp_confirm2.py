import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\order-confirm.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("async function runCompetition()")
end = text.find("runCompetition();", idx)
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-50):end+50])
print(safe)

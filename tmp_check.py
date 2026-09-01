with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find liveLaunch and startQuestions functions boundaries
idx_ll = text.find("    async function liveLaunch()")
idx_lc = text.find("\n    async function liveConnect()", idx_ll)

import re
safe = re.sub(r"[^\x00-\x7F]", "?", text[idx_ll:idx_lc])
print("Current liveLaunch:")
print(safe[:600])
print("---")
print("Length:", len(safe))

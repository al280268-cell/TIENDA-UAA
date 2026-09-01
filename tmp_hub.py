import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find the polling/state checking code
idx = text.find("mission_phase")
while idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-30):idx+200])
    print(f"--- {idx} ---")
    print(safe[:150])
    idx = text.find("mission_phase", idx+1)

import re
with open("old_quiz.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("store_mission")
if idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-300):idx+300])
    print(safe)
else:
    print("store_mission not found in old quiz.py")

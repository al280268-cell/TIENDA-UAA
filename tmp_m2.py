with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "ltimas Partidas" in l or "Ultimas Partidas" in l:
        import re
        print(f"Line {i+1}:", re.sub(r"[^\x00-\x7F]", "?", l.rstrip()))

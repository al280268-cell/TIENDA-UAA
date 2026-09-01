with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Remove Control en Vivo from sidebar (multiple possible formats)
for old in [
    '\n        <button class="nav-item" data-section="live" onclick="navTo(\'live\')">🎮 Control en Vivo</button>',
    '\n        <button class="nav-item" data-section="live" onclick="navTo(\'live\')">&#127918; Control en Vivo</button>',
]:
    if old in text:
        text = text.replace(old, "")
        print("Removed Control en Vivo nav item")

# Check if still there
import re
idx = text.find("Control en Vivo")
while idx != -1:
    safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-50):idx+150])
    print(f"Still found at {idx}:", safe[:100])
    idx = text.find("Control en Vivo", idx+1)

# Also fix Analitica → Informes if still not fixed
text = text.replace(">Analítica</button>", ">📊 Informes</button>")
text = text.replace(">Anal\u00edtica</button>", ">📊 Informes</button>")

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Done")

import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\admin.html", "r", encoding="utf-8") as f:
    text = f.read()

# Find active-game-panel precisely
idx = text.find('id="active-game-panel"')
safe = re.sub(r"[^\x00-\x7F]", "?", text[max(0,idx-30):idx+300])
print("Context:", safe)

# Find the next </div> that closes this element (need to count nesting)
start = idx - 10  # back to <div
content = text[start:]
depth = 0
close_pos = -1
for i, ch in enumerate(content):
    if content[i:i+4] == "<div":
        depth += 1
    elif content[i:i+6] == "</div>":
        depth -= 1
        if depth == 0:
            close_pos = start + i + 6
            break

print(f"start={start}, close={close_pos}")
agp_block = text[start:close_pos]
print("AGP block (first 200):", re.sub(r"[^\x00-\x7F]", "?", agp_block[:200]))

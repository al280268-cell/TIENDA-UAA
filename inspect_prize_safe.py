import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove emojis to print safely
safe_text = re.sub(r'[^\x00-\x7F]+', '', text)
lines = safe_text.split('\n')
for i, line in enumerate(lines):
    if 'prize-card' in line or 'prizes-grid' in line or 'action-bar' in line or 'selectPrize' in line:
        print(f"{i}: {line.strip()}")

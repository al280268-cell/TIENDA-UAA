with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'prize-card-ball' in line or 'prizes-grid' in line or 'selectPrize' in line:
            print(f"{i}: {line.strip()}")

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\prize.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(185, min(220, len(lines))):
        print(f"{i}: {lines[i].strip().encode('ascii', 'ignore').decode('ascii')}")

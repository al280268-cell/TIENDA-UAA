with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    content = f.read()

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub_backup.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Extract script only
import re
m = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if m:
    print('SCRIPT_START:')
    print(m.group(1))

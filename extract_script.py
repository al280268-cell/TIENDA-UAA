import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    html = f.read()

script = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if script:
    code = script.group(1)
    with open('hub_script.js', 'w', encoding='utf-8') as sf:
        sf.write(code)
    print("Script extracted to hub_script.js. Length:", len(code))
else:
    print("No script tag found!")

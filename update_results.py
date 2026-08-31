import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\results.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Apply spider-man background pattern to results page
text = text.replace(
    'body { background:#04040A; color:white; overflow-x:hidden; }',
    """body { background:#07070F; color:white; overflow-x:hidden; }
    body::after {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:0.5;
      background-image: url('img/web.svg');
      background-repeat:repeat; background-size:80px;
    }"""
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\results.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('results.html theme updated')

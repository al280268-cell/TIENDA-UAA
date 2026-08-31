import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\store.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Update background
text = re.sub(
    r'body\s*\{[^}]*background:[^}]*\}',
    '''body {
    background: #07070F;
    color: var(--text);
    font-family: var(--font);
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed; inset: 0;
    background: radial-gradient(ellipse 800px 500px at 0% 0%, rgba(230,36,41,0.14), transparent),
                radial-gradient(ellipse 700px 500px at 100% 100%, rgba(27,43,143,0.18), transparent);
    pointer-events: none; z-index: 0;
  }
  body::after {
    content: '';
    position: fixed; inset: 0;
    background-image: url('img/web.svg');
    background-repeat: repeat; background-size: 80px;
    opacity: 0.35; pointer-events: none; z-index: 0;
  }''',
    text, count=1, flags=re.DOTALL
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\store.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('store.html updated')

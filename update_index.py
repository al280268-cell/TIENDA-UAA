with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Add web pattern overlay to body
text = text.replace(
    'body {\n      background: var(--uaa-dark);\n      color: white;\n      overflow-x: hidden;\n    }',
    """body {
      background: #07070F;
      color: white;
      overflow-x: hidden;
    }
    body::after {
      content: '';
      position: fixed; inset: 0;
      background-image: url('img/web.svg');
      background-repeat: repeat;
      background-size: 80px;
      opacity: 0.45;
      pointer-events: none; z-index: 0;
    }"""
)

# Update title
text = text.replace(
    '<title>FERIA UAA',
    '<title>🕷 FERIA UAA'
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html updated')

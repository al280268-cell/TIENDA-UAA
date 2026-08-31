import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\store.html', 'r', encoding='utf-8') as f:
    text = f.read()

new_products = r"""const PRODUCTS = [
      { id:'p1', emoji:'🥤', name:'Cilindro UAA', category:'Lifestyle', price:150, rating:4.9, reviews:203, badge:'OFICIAL', badgeType:'gold', desc:'Cilindro deportivo oficial de la UAA. Perfecto para mantenerte hidratado en tus clases.', bg:'#1A0308', glowColor:'#E62429', tagColor:'#FF7A7D', accentHex:'e62429' },
      { id:'p2', emoji:'⚽', name:'Pelota UAA', category:'Deportes', price:250, rating:4.8, reviews:89, badge:'MÁS VENDIDO', badgeType:'gold', desc:'Pelota deportiva con el escudo de la Universidad. Ideal para las retas.', bg:'#0A1030', glowColor:'#2B5CE6', tagColor:'#7FA8FF', accentHex:'2b5ce6' },
      { id:'p3', emoji:'🐓', name:'Llavero de Gallo', category:'Accesorios', price:80, rating:4.9, reviews:156, badge:'TOP', badgeType:'gold', desc:'Llavero metálico oficial de la mascota de la UAA. Lleva el orgullo universitario.', bg:'#1A0308', glowColor:'#E62429', tagColor:'#FF7A7D', accentHex:'e62429' },
      { id:'p4', emoji:'✨', name:'Stickers Universitarios', category:'Accesorios', price:40, rating:4.7, reviews:321, badge:'', badgeType:'', desc:'Paquete de stickers para decorar tu laptop y libretas con tus carreras y mascota favorita.', bg:'#0A1030', glowColor:'#2B5CE6', tagColor:'#7FA8FF', accentHex:'2b5ce6' }
    ];"""

text = re.sub(r'const PRODUCTS = \[.*?\];', new_products, text, flags=re.DOTALL)

new_filters = r"""<div class="pill active" data-cat="all">Todos</div>
        <div class="pill" data-cat="Lifestyle">🥤 Lifestyle</div>
        <div class="pill" data-cat="Deportes">⚽ Deportes</div>
        <div class="pill" data-cat="Accesorios">🎒 Accesorios</div>"""

text = re.sub(r'<div class="pill active" data-cat="all">Todos</div>\s*<div class="pill" data-cat="[^"]+">.*?</div>\s*<div class="pill" data-cat="[^"]+">.*?</div>\s*<div class="pill" data-cat="[^"]+">.*?</div>', new_filters, text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\store.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated store.html products and filters")

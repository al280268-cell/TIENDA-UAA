import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\store.html', 'r', encoding='utf-8') as f:
    text = f.read()

original_products = r"""const PRODUCTS = [
        { id:'p1', emoji:'🎧', name:'Audífonos Bluetooth Pro', category:'Electrónica', price:899, rating:4.8, reviews:127, badge:'Más vendido', badgeType:'gold', desc:'Cancelación de ruido activa. 30h batería. Driver 40mm.', bg:'#1A0308', glowColor:'#E62429', tagColor:'#FF7A7D', accentHex:'e62429' },
        { id:'p2', emoji:'🎒', name:'Mochila Tech UAA', category:'Accesorios', price:599, rating:4.6, reviews:89, badge:'UAA Edition', badgeType:'gold', desc:'Puerto USB integrado. Compartimento laptop 15".', bg:'#0A1030', glowColor:'#2B5CE6', tagColor:'#7FA8FF', accentHex:'2b5ce6' },
        { id:'p3', emoji:'🥤', name:'Termo Premium 750ml', category:'Lifestyle', price:349, rating:4.9, reviews:203, badge:'Top Rated', badgeType:'gold', desc:'24h frío / 12h calor. Acero inoxidable grado alimenticio.', bg:'#1A0308', glowColor:'#E62429', tagColor:'#FF7A7D', accentHex:'e62429' },
        { id:'p4', emoji:'📷', name:'Webcam Full HD 1080p', category:'Electrónica', price:1299, rating:4.7, reviews:61, badge:'', badgeType:'', desc:'Autofocus inteligente. Micrófono integrado. Plug & play.', bg:'#0A1030', glowColor:'#2B5CE6', tagColor:'#7FA8FF', accentHex:'2b5ce6' },
        { id:'p5', emoji:'⌨️', name:'Teclado Mecánico RGB', category:'Electrónica', price:2499, rating:4.5, reviews:44, badge:'Premium', badgeType:'gold', desc:'Switches tácticos Cherry MX. Build full aluminio anodizado.', bg:'#1A0308', glowColor:'#E62429', tagColor:'#FF7A7D', accentHex:'e62429' },
        { id:'p6', emoji:'🖱️', name:'Ratón Inalámbrico Ergo', category:'Electrónica', price:449, rating:4.7, reviews:156, badge:'', badgeType:'', desc:'DPI ajustable hasta 3200. Batería 90 días. Ergonómico.', bg:'#0A1030', glowColor:'#2B5CE6', tagColor:'#7FA8FF', accentHex:'2b5ce6' },
        { id:'p7', emoji:'💡', name:'Lámpara LED Escritorio', category:'Lifestyle', price:289, rating:4.4, reviews:78, badge:'', badgeType:'', desc:'3 modos de luz. Puerto USB-C de carga integrado.', bg:'#1A0308', glowColor:'#E62429', tagColor:'#FF7A7D', accentHex:'e62429' },
        { id:'p8', emoji:'🔌', name:'Hub USB-C 7 en 1', category:'Electrónica', price:799, rating:4.6, reviews:93, badge:'Esencial', badgeType:'default', desc:'HDMI 4K, USB 3.0 ×3, SD, Ethernet, 100W Power Delivery.', bg:'#0A1030', glowColor:'#2B5CE6', tagColor:'#7FA8FF', accentHex:'2b5ce6' },
      ];"""

text = re.sub(r'const PRODUCTS = \[.*?\];', original_products, text, flags=re.DOTALL)

original_filters = r"""<div class="pill active" data-cat="all">Todos</div>
        <div class="pill" data-cat="Electrónica">💻 Electrónica</div>
        <div class="pill" data-cat="Accesorios">🎒 Accesorios</div>
        <div class="pill" data-cat="Lifestyle">☕ Lifestyle</div>"""

text = re.sub(r'<div class="pill active" data-cat="all">Todos</div>\s*<div class="pill" data-cat="[^"]+">.*?</div>\s*<div class="pill" data-cat="[^"]+">.*?</div>\s*<div class="pill" data-cat="[^"]+">.*?</div>', original_filters, text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\store.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Restored original store products.")

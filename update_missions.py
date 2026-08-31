import re, random
with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update MISSION_META for speed_search
text = re.sub(
    r'\"speed_search\":.*?\},',
    '\"speed_search\":   {\"emoji\": \"📈\", \"title\": \"Estrategia de Marketing\", \"desc\": \"Toma la mejor decisión para atraer clientes y aumentar tus ventas\", \"topic\": \"Marketing Digital\"},',
    text,
    flags=re.DOTALL
)

# 2. Replace _gen_speed_search body with Marketing logic
marketing_bank = '''
MARKETING_BANK = [
    {"difficulty":"media","scenario":"Tu tienda tiene muchas visitas pero pocas ventas.","question":"¿Qué métrica de marketing debes revisar primero?","options":[
        {"id":"A","text":"La tasa de conversión (CRO)"},
        {"id":"B","text":"El número de seguidores en Instagram"},
        {"id":"C","text":"El costo por clic (CPC) de tus anuncios"},
        {"id":"D","text":"El tiempo de carga de tu logo"}],
     "correct":"A","explanation":"La tasa de conversión te indica si tu tráfico está encontrando lo que busca y comprando.","concept":"Conversión"},
    {"difficulty":"media","scenario":"Quieres lanzar un producto nuevo para jóvenes universitarios.","question":"¿Qué canal de marketing es más efectivo?","options":[
        {"id":"A","text":"TikTok Ads y campañas de influencers"},
        {"id":"B","text":"Anuncios en el periódico local"},
        {"id":"C","text":"Llamadas telefónicas en frío (Telemarketing)"},
        {"id":"D","text":"Banners estáticos en sitios de noticias corporativas"}],
     "correct":"A","explanation":"El público universitario consume mayormente redes sociales dinámicas como TikTok.","concept":"Segmentación"},
    {"difficulty":"facil","scenario":"Tus clientes añaden productos pero abandonan el carrito.","question":"¿Qué acción de marketing es ideal aquí?","options":[
        {"id":"A","text":"Enviar un correo de 'Carrito Abandonado' con un descuento"},
        {"id":"B","text":"Borrar sus cuentas por inactividad"},
        {"id":"C","text":"Cambiar el logo de la tienda"},
        {"id":"D","text":"Imprimir folletos"}],
     "correct":"A","explanation":"El retargeting y los correos automáticos recuperan ventas perdidas.","concept":"Retargeting"}
]

def _gen_speed_search():
    # Ahora es una mision de Marketing
    import random
    q = random.choice(MARKETING_BANK)
    opts, correct = _shuffle_choices(q['options'], q['correct'])
    return {
        'scenario':    q['scenario'],
        'question':    q['question'],
        'options':     opts,
        'correct':     correct,
        'difficulty':  q.get('difficulty', 'media'),
        'explanation': q['explanation'],
        'concept':     q['concept'],
        'topic':       'Marketing Digital'
    }
'''

text = re.sub(
    r'def _gen_speed_search\(\):.*?(?=def _gen_)',
    marketing_bank + '\n',
    text,
    flags=re.DOTALL
)

# 3. Update get_pool to insert TWO of each mission
old_pool = 'others = [t for t in POOL_TYPES if t != "store_mission"]\\n            random.shuffle(others)'
new_pool = 'others = [t for t in POOL_TYPES if t != "store_mission"]\\n            others = others + others # 2 misiones de cada tipo\\n            random.shuffle(others)'
text = text.replace('others = [t for t in POOL_TYPES if t != "store_mission"]\n            random.shuffle(others)', 'others = [t for t in POOL_TYPES if t != "store_mission"]\n            others = others + others\n            random.shuffle(others)')

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'w', encoding='utf-8') as f:
    f.write(text)

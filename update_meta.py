import re
with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'\"speed_search\":\s*\{.*?\},',
    '\"speed_search\":   {\"emoji\": \"📈\", \"title\": \"Estrategia de Marketing\", \"desc\": \"Toma la mejor decisión para atraer clientes y aumentar tus ventas\", \"topic\": \"Marketing Digital\"},',
    text
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py', 'w', encoding='utf-8') as f:
    f.write(text)

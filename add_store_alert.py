import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Add alert to auto-redirect
text = text.replace(
    'console.log("Auto-redirecting to Store Mission...");',
    'alert("¡Felicidades! Has completado todas las materias. Ahora entrarás a tu misión final: El Simulador de E-Commerce de La Tienda UAA.");\n              console.log("Auto-redirecting to Store Mission...");'
)

# Add alert to clickAction when unlocked
text = text.replace(
    'btnText = isDone ? \'✓ COMPLETADA\' : \'ENTRAR A LA TIENDA →\';',
    'btnText = isDone ? \'✓ COMPLETADA\' : \'ENTRAR A LA TIENDA →\';\n             if(!isDone) clickAction = "alert(\'Entrarás al Simulador de E-Commerce de La Tienda UAA. Tu objetivo es realizar una compra.\'); startMission(\'" + m.mission_id + "\', \'" + m.mission_type + "\', \'" + m.status + "\')";'
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Added alerts for entering Store Mission")

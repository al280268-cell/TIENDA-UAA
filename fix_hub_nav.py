import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

patch = r"""
        let clickAction = isQuiz ? `window.location.href='mision.html?mission=${m.mission_id}'` : `startMission('${m.mission_id}', '${m.mission_type}', '${m.status}')`;
        
        let cardStyle = '';

        if (isStore) {
          if (!allQuizzesCompleted) {
             statusText = 'BLOQUEADA';
             statusClass = 'status-completed';
             btnText = '🔒 BLOQUEADA';
             btnClass = 'btn-done';
             clickAction = "alert('Debes completar todas las misiones de las Áreas de la Carrera para desbloquear La Tienda.')";
             cardStyle = 'opacity: 0.65; filter: grayscale(0.8);';
          } else {
             btnText = isDone ? '✓ COMPLETADA' : 'ENTRAR A LA TIENDA →';
             if(!isDone) btnClass = 'btn-store';
          }
        }
"""
text = re.sub(r'let clickAction = .*?(?=const card =)', patch.strip() + '\n\n        ', text, flags=re.DOTALL)

start_mission_patch = r"""
    async function startMission(id, type, status) {
        if (status === 'completed') return;
        sessionStorage.setItem('uaa_mission_id', id);
        sessionStorage.setItem('uaa_mission_type', type);
        if (player.code && player.id && status === 'available') {
          await api('POST', '/api/missions/start', { player_id:player.id, game_code:player.code, mission_id:id });
        }
        if (type === 'store_mission') window.location.href = 'store.html?mission=' + id;
        else window.location.href = 'game.html?mission=' + id;
    }
"""

text = re.sub(r'async function startMission\(id, type, status\) \{.*?\n    \}', start_mission_patch.strip(), text, flags=re.DOTALL)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed store navigation in hub.html")

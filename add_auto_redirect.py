import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Insert auto-redirect logic inside renderMissions
auto_redirect_patch = r"""
      let completedCount = 0;
      const quizMissions = missions.filter(m => m.is_quiz);
      const quizzesDone = quizMissions.filter(m => m.status === 'completed').length;
      const allQuizzesCompleted = (quizMissions.length > 0 && quizzesDone === quizMissions.length);
      
      const storeMissionObj = missions.find(m => m.mission_type === 'store_mission');
      if (allQuizzesCompleted && storeMissionObj && storeMissionObj.status === 'available') {
          if (!sessionStorage.getItem('store_auto_triggered_' + storeMissionObj.mission_id)) {
              sessionStorage.setItem('store_auto_triggered_' + storeMissionObj.mission_id, 'true');
              console.log("Auto-redirecting to Store Mission...");
              startMission(storeMissionObj.mission_id, storeMissionObj.mission_type, storeMissionObj.status);
              return;
          }
      }
"""

text = re.sub(
    r'      let completedCount = 0;\s*const quizMissions = missions\.filter\(m => m\.is_quiz\);\s*const quizzesDone = quizMissions\.filter\(m => m\.status === \'completed\'\)\.length;\s*const allQuizzesCompleted = \(quizMissions\.length > 0 && quizzesDone === quizMissions\.length\);', 
    auto_redirect_patch.strip(), 
    text
)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\frontend\hub.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Auto-redirect logic added to hub.html")

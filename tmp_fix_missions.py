import re
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py", "r", encoding="utf-8") as f:
    text = f.read()

old_val = """        if not row:
            return {"correct": False, "points": 0, "penalty": 0, "net": 0,
                    "explanation": "Misi\u00f3n no encontrada.", "all_complete": False,
                    "total_points": 0, "streak": 0, "new_rank": 0,
                    "concept": "", "topic": "E-Commerce"}"""

new_val = """        if not row:
            # Fallback for kahoot mode store_mission simulation
            if req.mission_type == "store_mission":
                base_points = 150
                res = await update_score(req.game_code, req.player_id, base_points, True)
                return {
                    "correct": True, "points": base_points, "penalty": 0, "net": base_points,
                    "explanation": "Simulaci\u00f3n de tienda completada.",
                    "all_complete": True,
                    "total_points": res.get("total_points", 0),
                    "streak": res.get("streak", 0),
                    "new_rank": 1,
                    "concept": "Customer Journey", "topic": "E-Commerce"
                }
            return {"correct": False, "points": 0, "penalty": 0, "net": 0,
                    "explanation": "Misi\u00f3n no encontrada.", "all_complete": False,
                    "total_points": 0, "streak": 0, "new_rank": 0,
                    "concept": "", "topic": "E-Commerce"}"""

text = text.replace(old_val, new_val)
with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\missions.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated missions.py")

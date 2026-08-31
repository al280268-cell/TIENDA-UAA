import re

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\quiz.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix indentation
patch = r'''
    total_points = None
    if gained and not already:
        try:
            update_score(req.game_code, req.player_id, gained, is_correct)
            # Send live update to the Ably channel so others see the score immediately
            from backend.app import publish_to_ably
            await publish_to_ably(f"game:{req.game_code}", "score_update", {
                "player_id": req.player_id,
                "points": gained
            })
            # Try to fetch it back for the local response
            from backend.core.game_state import get_game as get_gs_sync
            g = get_gs_sync(req.game_code)
            if g and req.player_id in g.players:
                total_points = g.players[req.player_id].points
        except Exception as e:
            print("Error updating score:", e)
            pass
'''

# Find the unindented block and replace it
unindented = "total_points = None\n    if gained and not already:\n        try:\n            update_score(req.game_code, req.player_id, gained, is_correct)"

text = text.replace(unindented, "    " + unindented)

with open(r'c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\quiz.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Indentation fixed.")

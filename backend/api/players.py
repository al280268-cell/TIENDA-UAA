from fastapi import APIRouter, HTTPException, Depends
from backend.core.security import get_current_player
from backend.core.game_state import get_game

router = APIRouter(prefix="/api/players", tags=["players"])

@router.post("/reconnect")
async def reconnect(player_info: dict = Depends(get_current_player)):
    code = player_info["game_code"]
    gs = get_game(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    return {
        "status": gs.status,
        "time_remaining": gs.time_remaining,
        "current_round": gs.current_round
    }

@router.post("/ready")
async def mark_ready(player_info: dict = Depends(get_current_player)):
    code = player_info["game_code"]
    gs = get_game(code)
    if gs and player_info["player_id"] in gs.players:
        gs.players[player_info["player_id"]].status = "ready"
    return {"success": True}

@router.get("/{player_id}/status")
async def get_status(player_id: str, player_info: dict = Depends(get_current_player)):
    if player_info["player_id"] != player_id:
        raise HTTPException(403, "Forbidden")
    code = player_info["game_code"]
    gs = get_game(code)
    if gs and player_id in gs.players:
        return vars(gs.players[player_id])
    raise HTTPException(404, "Player not found")

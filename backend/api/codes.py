import uuid
import time
from fastapi import APIRouter, HTTPException, Depends
from backend.models.rewards import CreateCodeRequest, ValidateCodeRequest, ValidateCodeResponse
from backend.core.database import get_db
from backend.core.security import get_admin, get_current_player
from backend.core.game_state import update_score
from backend.app import publish_to_ably

router = APIRouter(prefix="/api/codes", tags=["codes"])

@router.post("/validate", response_model=ValidateCodeResponse)
async def validate_code(req: ValidateCodeRequest, player_info: dict = Depends(get_current_player)):
    if player_info["player_id"] != req.player_id:
        raise HTTPException(403, "Forbidden")
        
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM codes WHERE code = ?", (req.code,))
        code_data = await cursor.fetchone()
        
        if not code_data:
            return ValidateCodeResponse(valid=False, points=0, message="Invalid code")
            
        if code_data["expires_at"] < time.time():
            return ValidateCodeResponse(valid=False, points=0, message="Code expired")
            
        if code_data["uses"] >= code_data["max_uses"]:
            return ValidateCodeResponse(valid=False, points=0, message="Code usage limit reached")
            
        await db.execute("UPDATE codes SET uses = uses + 1 WHERE code = ?", (req.code,))
        await db.commit()
        
    update_score(req.game_code, req.player_id, code_data["reward_points"], True)
    
    from backend.core.game_state import get_game
    gs = get_game(req.game_code)
    player = gs.players.get(req.player_id)
    
    await publish_to_ably(f"game:{req.game_code}", "score_update", {
        "player_id": req.player_id,
        "points": player.points,
        "rank": player.rank
    })
    
    return ValidateCodeResponse(valid=True, points=code_data["reward_points"], message="Code validated successfully")

@router.post("/create")
async def create_code(req: CreateCodeRequest, admin=Depends(get_admin)):
    expires_at = time.time() + (req.expires_in_minutes * 60)
    async with get_db() as db:
        await db.execute(
            """INSERT INTO codes (id, code, reward_points, mission_type, max_uses, expires_at, created_at, game_code)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), req.code, req.reward_points, req.mission_type, req.max_uses, expires_at, time.time(), req.game_code)
        )
        await db.commit()
    return {"success": True, "code": req.code}

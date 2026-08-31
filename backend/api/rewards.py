import uuid
import time
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from backend.models.rewards import RewardResponse, ClaimRewardRequest, ClaimRewardResponse
from backend.core.database import get_db
from backend.core.security import get_admin, get_current_player
from backend.core.matchmaking import generate_claim_code
from backend.app import publish_to_ably
from backend.core.game_state import get_game

router = APIRouter(prefix="/api/rewards", tags=["rewards"])

# Premios por defecto (se usan si la DB está vacía)
DEFAULT_REWARDS = [
    {"id": "agua",     "name": "Botella de Agua", "emoji": "\U0001f4a7", "description": "Botella de agua fría",
     "stock_initial": 50, "stock_remaining": 50, "min_points": 0, "min_rank": None, "game_code": None, "disabled": 0},
    {"id": "pelota",   "name": "Pelota",           "emoji": "\u26bd",     "description": "Pelota de hule",
     "stock_initial": 50, "stock_remaining": 50, "min_points": 0, "min_rank": None, "game_code": None, "disabled": 0},
    {"id": "sticker1", "name": "Sticker UAA",      "emoji": "\U0001f3f7\ufe0f",  "description": "Pack de stickers exclusivos UAA",
     "stock_initial": 100,"stock_remaining": 100,"min_points": 0, "min_rank": None, "game_code": None, "disabled": 0},
    {"id": "sticker2", "name": "Sticker E-Commerce","emoji": "\U0001f6cd\ufe0f", "description": "Sticker edición Feria 2026",
     "stock_initial": 100,"stock_remaining": 100,"min_points": 0, "min_rank": None, "game_code": None, "disabled": 0},
]

async def _ensure_defaults():
    """Inserta los premios por defecto si la tabla está vacía."""
    async with get_db() as db:
        cur = await db.execute("SELECT COUNT(*) FROM rewards")
        row = await cur.fetchone()
        if row and row[0] == 0:
            for r in DEFAULT_REWARDS:
                try:
                    await db.execute(
                        "INSERT OR IGNORE INTO rewards (id, name, emoji, description, stock_initial, stock_remaining, min_points, min_rank, game_code, disabled) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (r["id"], r["name"], r["emoji"], r.get("description",""),
                         r["stock_initial"], r["stock_remaining"],
                         r["min_points"], r["min_rank"], r["game_code"], r.get("disabled",0))
                    )
                except Exception:
                    pass
            await db.commit()

@router.get("")
@router.get("/")
async def list_rewards(game_code: str = "", include_disabled: bool = False):
    """Lista premios. Oculta los desactivados a jugadores (include_disabled=false)."""
    await _ensure_defaults()
    try:
        async with get_db() as db:
            if game_code:
                cursor = await db.execute("SELECT * FROM rewards WHERE game_code = ?", (game_code,))
            else:
                cursor = await db.execute("SELECT * FROM rewards")
            rows = await cursor.fetchall()
            if rows:
                result = [dict(r) for r in rows]
                if not include_disabled:
                    result = [r for r in result if not r.get("disabled", 0)]
                return result
    except Exception:
        pass
    return [r for r in DEFAULT_REWARDS if not r.get("disabled", 0)]

@router.get("/admin/all")
async def list_rewards_admin(admin=Depends(get_admin)):
    """Admin: lista TODOS los premios incluyendo desactivados."""
    await _ensure_defaults()
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM rewards")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

class ToggleRewardRequest(BaseModel):
    reward_id: str
    disabled: bool

@router.post("/admin/toggle")
async def toggle_reward(req: ToggleRewardRequest, admin=Depends(get_admin)):
    """Admin: activa o desactiva un premio en la tienda."""
    async with get_db() as db:
        await db.execute(
            "UPDATE rewards SET disabled = ? WHERE id = ?",
            (1 if req.disabled else 0, req.reward_id)
        )
        await db.commit()
    return {"success": True, "reward_id": req.reward_id, "disabled": req.disabled}

class UpdateStockRequest(BaseModel):
    reward_id: str
    stock: int

@router.post("/admin/stock")
async def update_stock(req: UpdateStockRequest, admin=Depends(get_admin)):
    """Admin: ajusta el stock de un premio."""
    async with get_db() as db:
        await db.execute(
            "UPDATE rewards SET stock_remaining = ? WHERE id = ?",
            (max(0, req.stock), req.reward_id)
        )
        await db.commit()
    return {"success": True}

@router.post("/claim")
async def claim_reward(req: ClaimRewardRequest):
    """Reclama un premio. Genera claim_code siempre."""
    claim_code = generate_claim_code()
    try:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM rewards WHERE id = ?", (req.reward_id,))
            reward = await cursor.fetchone()
            if reward and reward["stock_remaining"] > 0:
                await db.execute(
                    "UPDATE rewards SET stock_remaining = stock_remaining - 1 "
                    "WHERE id = ? AND stock_remaining > 0",
                    (req.reward_id,)
                )
            await db.execute(
                "INSERT INTO redemptions (id, player_id, reward_id, game_code, claim_code, claimed_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), req.player_id, req.reward_id, req.game_code, claim_code, time.time())
            )
            await db.commit()
    except Exception:
        pass
    try:
        await publish_to_ably(f"game:{req.game_code}", "reward_claimed", {
            "player_id": req.player_id, "reward_id": req.reward_id, "claim_code": claim_code
        })
    except Exception:
        pass
    return ClaimRewardResponse(success=True, claim_code=claim_code, message="Premio reclamado exitosamente")

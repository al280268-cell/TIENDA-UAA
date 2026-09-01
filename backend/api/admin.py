from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.core.config import settings
from backend.core.security import create_admin_token, get_admin
from backend.core.database import get_db
from backend.core.game_state import (
    get_game, remove_player, get_round_status, get_leaderboard, recalculate_ranks
)
from backend.app import publish_to_ably

router = APIRouter(prefix="/api/admin", tags=["admin"])


class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    if req.password != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "Invalid password")
    return {"admin_token": create_admin_token()}


# ── Simulator toggle ─────────────────────────────────────────────────────────
async def _get_simulator_enabled() -> bool:
    async with get_db() as db:
        cur = await db.execute("SELECT value FROM app_settings WHERE key='simulator_enabled'")
        row = await cur.fetchone()
        return bool(row) and row["value"] == "1"

@router.get("/simulator")
async def get_simulator_state():
    return {"enabled": await _get_simulator_enabled()}

class SimulatorToggleRequest(BaseModel):
    enabled: bool

@router.post("/simulator")
async def set_simulator_state(req: SimulatorToggleRequest, admin=Depends(get_admin)):
    async with get_db() as db:
        await db.execute(
            "INSERT INTO app_settings (key, value) VALUES ('simulator_enabled', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("1" if req.enabled else "0",),
        )
        await db.commit()
    return {"enabled": req.enabled}


# ── Games list ────────────────────────────────────────────────────────────────
@router.get("/games")
async def list_games(admin=Depends(get_admin)):
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM games ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ── Game detail ───────────────────────────────────────────────────────────────
@router.get("/game/{code}")
async def get_game_detail(code: str, admin=Depends(get_admin)):
    from backend.api.games import _ensure_in_memory
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    return {
        "code": gs.game_code,
        "name": gs.name,
        "status": gs.status,
        "players": [vars(p) for p in gs.players.values()],
        "time_remaining": gs.time_remaining,
        "mission_phase": gs.mission_phase,
        "current_mission_index": gs.current_mission_index,
    }


# ── LIVE monitoring (Kahoot admin panel) ─────────────────────────────────────
@router.get("/game/{code}/live")
async def get_live_status(code: str, admin=Depends(get_admin)):
    """Full real-time status for the admin control panel."""
    from backend.api.games import _ensure_in_memory
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")

    from backend.core.game_state import get_mission_time_remaining
    round_info = get_round_status(code)
    leaderboard = [vars(p) for p in get_leaderboard(code)]

    current_mission_id = None
    if 0 <= gs.current_mission_index < len(gs.missions_order):
        current_mission_id = gs.missions_order[gs.current_mission_index]

    return {
        "game_code":             code,
        "game_name":             gs.name,
        "status":                gs.status,
        "mission_phase":         gs.mission_phase,
        "current_mission_index": gs.current_mission_index,
        "current_mission_id":    current_mission_id,
        "total_missions":        len(gs.missions_order),
        "missions_order":        gs.missions_order,
        "mission_time_remaining": get_mission_time_remaining(code),
        "mission_duration_sec":  gs.mission_duration_sec,
        "mission_locked":        gs.mission_locked,
        "player_count":          len(gs.players),
        "round_status":          round_info,
        "leaderboard":           leaderboard,
    }


# ── Inventory management ──────────────────────────────────────────────────────
@router.get("/inventory")
async def get_inventory(admin=Depends(get_admin)):
    """Full inventory with initial vs current stock."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, name, emoji, description, stock_initial, stock_remaining, "
            "disabled, game_code FROM rewards ORDER BY name"
        )
        rows = await cursor.fetchall()
        result = []
        for r in rows:
            row = dict(r)
            row["sold"] = row["stock_initial"] - row["stock_remaining"]
            row["status"] = "AGOTADO" if row["stock_remaining"] <= 0 else "Disponible"
            result.append(row)
        return result

class UpdateInventoryRequest(BaseModel):
    reward_id: str
    stock_remaining: int          # Only current stock changes
    disabled: Optional[bool] = None

@router.post("/inventory/update")
async def update_inventory(req: UpdateInventoryRequest, admin=Depends(get_admin)):
    """Update only stock_remaining. stock_initial is never changed."""
    async with get_db() as db:
        if req.disabled is not None:
            await db.execute(
                "UPDATE rewards SET stock_remaining=?, disabled=? WHERE id=?",
                (req.stock_remaining, 1 if req.disabled else 0, req.reward_id)
            )
        else:
            await db.execute(
                "UPDATE rewards SET stock_remaining=? WHERE id=?",
                (req.stock_remaining, req.reward_id)
            )
        await db.commit()
    return {"success": True, "stock_remaining": req.stock_remaining}


# ── Player management ─────────────────────────────────────────────────────────
class KickPlayerRequest(BaseModel):
    game_code: str
    player_id: str

@router.post("/player/kick")
async def kick_player(req: KickPlayerRequest, admin=Depends(get_admin)):
    from backend.api.games import _ensure_in_memory
    await _ensure_in_memory(req.game_code)
    remove_player(req.game_code, req.player_id)
    async with get_db() as db:
        await db.execute("UPDATE players SET status='kicked' WHERE id=?", (req.player_id,))
        await db.commit()
    await publish_to_ably(f"game:{req.game_code}", "player_kicked", {"player_id": req.player_id})
    return {"success": True}


# ── Time management ───────────────────────────────────────────────────────────
class AddTimeRequest(BaseModel):
    game_code: str
    seconds: int

@router.post("/time/add")
async def add_time(req: AddTimeRequest, admin=Depends(get_admin)):
    from backend.api.games import _ensure_in_memory
    gs = await _ensure_in_memory(req.game_code)
    if gs and gs.time_remaining is not None:
        gs.time_remaining += req.seconds
        return {"success": True, "time_remaining": gs.time_remaining}
    raise HTTPException(400, "Cannot add time")


# ── Analytics ─────────────────────────────────────────────────────────────────
@router.get("/analytics")
async def get_analytics(admin=Depends(get_admin)):
    async with get_db() as db:
        cursor = await db.execute("SELECT COUNT(*) as total FROM players")
        row = await cursor.fetchone()
        return {"total_participants": row["total"] if row else 0}


# ── Reward stock (legacy) ─────────────────────────────────────────────────────
class UpdateRewardRequest(BaseModel):
    reward_id: str
    stock: int

@router.post("/rewards/update")
async def update_reward_stock(req: UpdateRewardRequest, admin=Depends(get_admin)):
    async with get_db() as db:
        await db.execute(
            "UPDATE rewards SET stock_remaining=? WHERE id=?",
            (req.stock, req.reward_id)
        )
        await db.commit()
    return {"success": True}


# ── Codes ─────────────────────────────────────────────────────────────────────
@router.get("/codes")
async def list_codes(admin=Depends(get_admin)):
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM codes ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

class CreateCodeRequest(BaseModel):
    code: str
    reward_points: int = 100
    max_uses: int = 1
    game_code: str = None
    expires_minutes: int = None

@router.post("/codes/create")
async def create_code(req: CreateCodeRequest, admin=Depends(get_admin)):
    import uuid, time as _time
    expires_at = None
    if req.expires_minutes:
        expires_at = _time.time() + (req.expires_minutes * 60)
    async with get_db() as db:
        try:
            await db.execute(
                """INSERT INTO codes (id, code, reward_points, max_uses, uses, expires_at, created_at, game_code)
                   VALUES (?, ?, ?, ?, 0, ?, ?, ?)""",
                (str(uuid.uuid4()), req.code.upper(), req.reward_points,
                 req.max_uses, expires_at, _time.time(), req.game_code)
            )
            await db.commit()
        except Exception as e:
            raise HTTPException(400, f"Error creating code: {str(e)}")
    return {"success": True, "code": req.code.upper()}

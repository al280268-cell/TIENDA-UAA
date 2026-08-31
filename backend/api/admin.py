from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.core.config import settings
from backend.core.security import create_admin_token, get_admin
from backend.core.database import get_db
from backend.core.game_state import get_game, remove_player
from backend.app import publish_to_ably

router = APIRouter(prefix="/api/admin", tags=["admin"])

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    if req.password != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "Invalid password")
    return {"admin_token": create_admin_token()}

# ── Interruptor del SIMULADOR (controlado del lado del servidor) ──────────────
async def _get_simulator_enabled() -> bool:
    async with get_db() as db:
        cur = await db.execute("SELECT value FROM app_settings WHERE key='simulator_enabled'")
        row = await cur.fetchone()
        return bool(row) and row["value"] == "1"

@router.get("/simulator")
async def get_simulator_state():
    """Público (solo lectura): las páginas consultan si el simulador está activo."""
    return {"enabled": await _get_simulator_enabled()}

class SimulatorToggleRequest(BaseModel):
    enabled: bool

@router.post("/simulator")
async def set_simulator_state(req: SimulatorToggleRequest, admin=Depends(get_admin)):
    """Solo admin: activa/desactiva el simulador. Requiere token de administrador."""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO app_settings (key, value) VALUES ('simulator_enabled', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("1" if req.enabled else "0",),
        )
        await db.commit()
    return {"enabled": req.enabled}

@router.get("/games")
async def list_games(admin=Depends(get_admin)):
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM games ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

@router.get("/game/{code}")
async def get_game_detail(code: str, admin=Depends(get_admin)):
    gs = get_game(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    return {
        "code": gs.game_code,
        "name": gs.name,
        "status": gs.status,
        "players": [vars(p) for p in gs.players.values()],
        "time_remaining": gs.time_remaining
    }

class KickPlayerRequest(BaseModel):
    game_code: str
    player_id: str

@router.post("/player/kick")
async def kick_player(req: KickPlayerRequest, admin=Depends(get_admin)):
    remove_player(req.game_code, req.player_id)
    async with get_db() as db:
        await db.execute("UPDATE players SET status = 'kicked' WHERE id = ?", (req.player_id,))
        await db.commit()
    await publish_to_ably(f"game:{req.game_code}", "player_kicked", {"player_id": req.player_id})
    return {"success": True}

class AddTimeRequest(BaseModel):
    game_code: str
    seconds: int

@router.post("/time/add")
async def add_time(req: AddTimeRequest, admin=Depends(get_admin)):
    gs = get_game(req.game_code)
    if gs and gs.time_remaining is not None:
        gs.time_remaining += req.seconds
        return {"success": True, "time_remaining": gs.time_remaining}
    raise HTTPException(400, "Cannot add time")

@router.post("/mission/special")
async def trigger_special(game_code: str, admin=Depends(get_admin)):
    await publish_to_ably(f"game:{game_code}", "special_mission_triggered", {})
    return {"success": True}

@router.get("/analytics")
async def get_analytics(admin=Depends(get_admin)):
    async with get_db() as db:
        cursor = await db.execute("SELECT COUNT(*) as total FROM players")
        row = await cursor.fetchone()
        return {"total_participants": row["total"] if row else 0}

class UpdateRewardRequest(BaseModel):
    reward_id: str
    stock: int

@router.post("/rewards/update")
async def update_reward_stock(req: UpdateRewardRequest, admin=Depends(get_admin)):
    async with get_db() as db:
        await db.execute("UPDATE rewards SET stock_remaining = ? WHERE id = ?", (req.stock, req.reward_id))
        await db.commit()
    return {"success": True}

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
            from fastapi import HTTPException
            raise HTTPException(400, f"Error creating code: {str(e)}")
    return {"success": True, "code": req.code.upper()}

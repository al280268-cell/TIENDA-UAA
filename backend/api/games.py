import random
import time
import uuid
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from backend.models.game import CreateGameRequest, JoinGameRequest, GameResponse, StartGameRequest
from backend.core.matchmaking import generate_game_code, generate_player_id
from backend.core.security import create_admin_token, create_player_token, get_admin
from backend.core.database import get_db
from backend.core.game_state import (
    create_game, get_game, set_status, add_player, PlayerState,
    start_mission_round, lock_mission_round, get_mission_time_remaining,
    get_round_status, recalculate_ranks, get_leaderboard
)
from backend.app import publish_to_ably

router = APIRouter(prefix="/api/games", tags=["games"])


class MissionStartRequest(BaseModel):
    mission_id: Optional[str] = None   # If None, server picks next in order
    duration_sec: Optional[int] = None  # Override default duration

class MissionDurationRequest(BaseModel):
    duration_sec: int


# ── Reconstruct game from DB when RAM is empty (handles server restarts) ──────
async def _ensure_in_memory(code: str):
    """Returns GameState from RAM. If not there (server restarted), rebuilds from DB."""
    from backend.core.game_state import _games
    gs = get_game(code)
    if gs:
        return gs

    async with get_db() as db:
        cur = await db.execute("SELECT * FROM games WHERE code=?", (code,))
        row = await cur.fetchone()
        if not row:
            return None
        row = dict(row)

        # Reconstruct GameState
        gs = create_game(code, {
            "name":               row.get("name", "Game"),
            "difficulty":         row.get("difficulty", "normal"),
            "duration_seconds":   row.get("duration_seconds", 480),
            "rounds":             row.get("rounds", 5),
            "max_players":        row.get("max_players", 20),
            "mission_duration_sec": row.get("mission_duration_sec", 60),
        })
        gs.status      = row.get("status", "waiting")
        gs.started_at  = row.get("started_at")
        if gs.status == "finished":
            gs.mission_phase = "finished"   # so hub.html redirects to results
        elif gs.status == "active":
            gs.mission_phase = "lobby"      # safe default: admin will re-launch

        # Reload players from DB
        pcur = await db.execute(
            "SELECT * FROM players WHERE game_code=? AND (status IS NULL OR status!='kicked')",
            (code,)
        )
        for pr in await pcur.fetchall():
            p = PlayerState(
                player_id       = pr["id"],
                name            = pr["name"],
                avatar_color    = pr["avatar_color"],
                avatar_initials = pr["avatar_initials"],
            )
            add_player(code, p)

        return gs


# ── CREAR PARTIDA ─────────────────────────────────────────────────────────────
@router.post("/create")
async def create_new_game(req: CreateGameRequest):
    game_code   = generate_game_code()
    admin_token = create_admin_token()
    max_pl = req.max_players or 30

    async with get_db() as db:
        await db.execute(
            """INSERT INTO games (id, code, name, difficulty, max_players,
               duration_seconds, rounds, prizes_config, created_at,
               mission_duration_sec)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), game_code, req.name, req.difficulty, max_pl,
             req.duration_seconds, req.rounds, json.dumps([]), time.time(),
             getattr(req, 'mission_duration_sec', 60))
        )
        await db.commit()

    create_game(game_code, {**req.dict(), "max_players": max_pl,
                             "mission_duration_sec": getattr(req, 'mission_duration_sec', 60)})
    return {"game_code": game_code, "admin_token": admin_token}


# ── UNIRSE ────────────────────────────────────────────────────────────────────
@router.post("/join")
async def join_game(req: JoinGameRequest):
    gs = await _ensure_in_memory(req.game_code)
    if not gs or gs.status not in ("waiting", "active"):
        raise HTTPException(400, "Game not found or not waiting")
    if len(gs.players) >= gs.max_players:
        raise HTTPException(400, "Game is full")

    for p in gs.players.values():
        if p.name == req.player_name:
            raise HTTPException(400, "Name already taken in this game")

    player_id = generate_player_id()
    colors = ["#FF5733","#33FF57","#3357FF","#F1C40F","#9B59B6",
              "#1ABC9C","#E67E22","#E74C3C","#34495E","#2ECC71","#3498DB","#95A5A6"]
    avatar_color    = random.choice(colors)
    avatar_initials = req.player_name[:2].upper()

    player_state = PlayerState(player_id, req.player_name, avatar_color, avatar_initials)
    add_player(req.game_code, player_state)

    async with get_db() as db:
        await db.execute(
            """INSERT INTO players (id, game_code, name, avatar_color, avatar_initials, joined_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (player_id, req.game_code, req.player_name, avatar_color, avatar_initials, time.time())
        )
        await db.commit()

    player_token = create_player_token(player_id, req.game_code)

    await publish_to_ably(f"game:{req.game_code}", "player_joined", {
        "player_id": player_id,
        "name": req.player_name,
        "avatar_color": avatar_color,
        "avatar_initials": avatar_initials
    })

    return {
        "player_token": player_token,
        "player_id": player_id,
        "avatar_color": avatar_color,
        "avatar_initials": avatar_initials
    }


# ── ESTADO DE LA PARTIDA ──────────────────────────────────────────────────────
@router.get("/{code}/state")
async def get_game_state_endpoint(code: str):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")

    # Time remaining for the overall session
    remaining = gs.time_remaining
    if gs.status == "active" and gs.started_at:
        remaining = max(0, int(round(gs.duration_seconds - (time.time() - gs.started_at))))
        gs.time_remaining = remaining
        if remaining <= 0 and gs.status != "finished":
            gs.status = "finished"

    # Mission-level time remaining (authoritative)
    mission_time_remaining = get_mission_time_remaining(code)

    # Build current mission info
    current_mission_id = None
    if 0 <= gs.current_mission_index < len(gs.missions_order):
        current_mission_id = gs.missions_order[gs.current_mission_index]

    players_data = []
    for p in gs.players.values():
        players_data.append({
            "player_id": p.player_id,
            "name": p.name,
            "avatar_color": p.avatar_color,
            "avatar_initials": p.avatar_initials,
            "points": p.points,
            "rank": p.rank,
            "streak": p.streak,
            "missions_completed": p.missions_completed,
            "status": p.status,
            "round_answered": p.round_answered,
        })

    return {
        "game_code":    code,
        "status":       gs.status,
        "difficulty":   gs.difficulty,
        "total_rounds": gs.total_rounds,
        "current_round": gs.current_round,
        "max_players":  gs.max_players,
        "duration_seconds": gs.duration_seconds,
        "time_remaining":   remaining,
        "players":      players_data,
        # Kahoot sync fields
        "mission_phase":         gs.mission_phase,
        "current_mission_index": gs.current_mission_index,
        "current_mission_id":    current_mission_id,
        "total_missions":        len(gs.missions_order),
        "missions_order":        gs.missions_order,
        "mission_start_ts":      gs.mission_start_ts,
        "mission_duration_sec":  gs.mission_duration_sec,
        "mission_time_remaining": mission_time_remaining,
        "mission_locked":        gs.mission_locked,
        # Store simulation phase
        "store_done_count":  len(gs.store_done_players),
        "store_total":       len(gs.players),
        "store_timeout_at":  (gs.store_simulation_started_at + 120) if gs.store_simulation_started_at else None,
    }


class StoreDoneRequest(BaseModel):
    player_id: str

# ── PLAYER MARKS STORE SIMULATION DONE ───────────────────────────────────────
@router.post("/{code}/store_done")
async def mark_store_done(code: str, req: StoreDoneRequest):
    """Called by each player when they finish the store simulation checkout."""
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")

    if req.player_id not in gs.players:
        raise HTTPException(400, "Player not in this game")

    gs.store_done_players.add(req.player_id)

    total   = len(gs.players)
    done    = len(gs.store_done_players)
    all_done = done >= total

    return {
        "success":   True,
        "done_count": done,
        "total":     total,
        "all_done":  all_done,
    }


# ── GET STORE SIMULATION STATUS ───────────────────────────────────────────────
@router.get("/{code}/store_status")
async def get_store_status(code: str):
    """Polling endpoint for players waiting in the store simulation phase."""
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")

    total    = len(gs.players)
    done     = len(gs.store_done_players)
    elapsed  = (time.time() - gs.store_simulation_started_at) if gs.store_simulation_started_at else 0
    timed_out = elapsed >= 120

    all_done = (total > 0 and done >= total) or timed_out or gs.mission_phase == "finished"

    return {
        "mission_phase": gs.mission_phase,
        "all_done":      all_done,
        "done_count":    done,
        "total":         total,
        "seconds_left":  max(0, int(120 - elapsed)),
    }


# ── INICIAR PARTIDA (global) ──────────────────────────────────────────────────

@router.post("/{code}/start")
async def start_game(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found in DB")
    if gs.status == "finished":
        raise HTTPException(400, "Game already finished")

    gs.status       = "active"
    gs.started_at   = time.time()
    gs.time_remaining = gs.duration_seconds
    gs.mission_phase  = "lobby"

    async with get_db() as db:
        await db.execute(
            "UPDATE games SET status='active', started_at=?, time_remaining=? WHERE code=?",
            (gs.started_at, gs.time_remaining, code)
        )
        await db.commit()

    await publish_to_ably(f"game:{code}", "game_started", {
        "game_code": code,
        "duration": gs.duration_seconds
    })
    return {"success": True}


class LaunchRequest(BaseModel):
    duration_sec: int = 30          # seconds per mission
    results_sec: int = 5            # seconds to show results between missions
    missions: Optional[List[str]] = None  # custom mission order; default: m1-m6

# ── LANZAR JUEGO COMPLETO (1 botón = juego automático tipo Kahoot) ────────────
@router.post("/{code}/launch")
async def launch_game(code: str, req: LaunchRequest, admin=Depends(get_admin)):
    """
    One-click: starts game + mission 1. The background timer handles all
    subsequent missions automatically. Admin never needs to click 'next'.
    """
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found in DB")
    if gs.status == "finished":
        raise HTTPException(400, "Game already finished")

    # Configure
    DEFAULT_MISSIONS = ["m1", "m2", "m3", "m4", "m5", "m6"]
    gs.missions_order        = req.missions or DEFAULT_MISSIONS
    gs.mission_duration_sec  = req.duration_sec
    gs.results_display_sec   = req.results_sec
    gs.status                = "active"
    gs.started_at            = time.time()
    gs.time_remaining        = gs.duration_seconds

    async with get_db() as db:
        await db.execute(
            "UPDATE games SET status='active', started_at=?, time_remaining=? WHERE code=?",
            (gs.started_at, gs.time_remaining, code)
        )
        await db.commit()

    # Start mission 0 immediately
    start_mission_round(code, 0, gs.missions_order[0])

    await publish_to_ably(f"game:{code}", "mission_started", {
        "mission_index":  0,
        "mission_id":     gs.missions_order[0],
        "duration_sec":   gs.mission_duration_sec,
        "start_ts":       gs.mission_start_ts,
        "total_missions": len(gs.missions_order),
    })

    return {
        "success":        True,
        "mission_id":     gs.missions_order[0],
        "duration_sec":   gs.mission_duration_sec,
        "total_missions": len(gs.missions_order),
        "start_ts":       gs.mission_start_ts,
    }


# ── INICIAR MISIÓN (admin lanza ronda) ───────────────────────────────────────
@router.post("/{code}/mission/start")
async def admin_start_mission(code: str, req: MissionStartRequest, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    if gs.status == "finished":
        raise HTTPException(400, "Game already finished")

    # Auto-start the game if still waiting
    if gs.status == "waiting":
        gs.status       = "active"
        gs.started_at   = time.time()
        gs.time_remaining = gs.duration_seconds
        async with get_db() as db:
            await db.execute(
                "UPDATE games SET status='active', started_at=?, time_remaining=? WHERE code=?",
                (gs.started_at, gs.time_remaining, code)
            )
            await db.commit()
        await publish_to_ably(f"game:{code}", "game_started", {"game_code": code})

    # Default missions order if not set yet
    DEFAULT_MISSIONS = ["m1", "m2", "m3", "m4", "m5", "m6"]
    if not gs.missions_order:
        gs.missions_order = DEFAULT_MISSIONS[:]

    # Set duration override if provided
    if req.duration_sec:
        gs.mission_duration_sec = req.duration_sec

    # Determine which mission to start
    if req.mission_id:
        mission_id = req.mission_id
        if mission_id not in gs.missions_order:
            gs.missions_order.append(mission_id)
        mission_index = gs.missions_order.index(mission_id)
    else:
        # First call starts mission 0; subsequent calls advance
        if gs.current_mission_index < 0:
            mission_index = 0
        else:
            mission_index = gs.current_mission_index + 1
        if mission_index >= len(gs.missions_order):
            raise HTTPException(400, "No more missions in order")
        mission_id = gs.missions_order[mission_index]

    start_mission_round(code, mission_index, mission_id)
    gs.status = "active"

    await publish_to_ably(f"game:{code}", "mission_started", {
        "mission_index":    mission_index,
        "mission_id":       mission_id,
        "duration_sec":     gs.mission_duration_sec,
        "start_ts":         gs.mission_start_ts,
        "total_missions":   len(gs.missions_order),
    })

    return {
        "success": True,
        "mission_index": mission_index,
        "mission_id": mission_id,
        "duration_sec": gs.mission_duration_sec,
        "start_ts": gs.mission_start_ts,
    }


# ── CONFIGURAR ORDEN DE MISIONES ─────────────────────────────────────────────
class SetMissionsOrderRequest(BaseModel):
    missions: List[str]   # ordered list of mission IDs
    mission_duration_sec: Optional[int] = None

@router.post("/{code}/missions/order")
async def set_missions_order(code: str, req: SetMissionsOrderRequest, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    gs.missions_order = req.missions
    if req.mission_duration_sec:
        gs.mission_duration_sec = req.mission_duration_sec
    return {"success": True, "missions_order": gs.missions_order}


# ── BLOQUEAR MISIÓN (tiempo terminado) ───────────────────────────────────────
@router.post("/{code}/mission/lock")
async def admin_lock_mission(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    summary = lock_mission_round(code)
    leaderboard = [vars(p) for p in get_leaderboard(code)]

    await publish_to_ably(f"game:{code}", "mission_locked", {
        "mission_index": gs.current_mission_index,
        "results": summary.get("results", []),
        "leaderboard": leaderboard,
    })
    return {"success": True, **summary}


# ── SIGUIENTE MISIÓN ──────────────────────────────────────────────────────────
@router.post("/{code}/mission/next")
async def admin_next_mission(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")

    if not gs.missions_order:
        gs.missions_order = ["m1", "m2", "m3", "m4", "m5", "m6"]

    next_index = gs.current_mission_index + 1
    if next_index >= len(gs.missions_order):
        # All missions done → end game
        return await _finish_game(code, gs)


    mission_id = gs.missions_order[next_index]
    start_mission_round(code, next_index, mission_id)

    await publish_to_ably(f"game:{code}", "mission_started", {
        "mission_index":  next_index,
        "mission_id":     mission_id,
        "duration_sec":   gs.mission_duration_sec,
        "start_ts":       gs.mission_start_ts,
        "total_missions": len(gs.missions_order),
    })

    return {
        "success": True,
        "mission_index": next_index,
        "mission_id": mission_id,
        "start_ts": gs.mission_start_ts,
    }


async def _finish_game(code: str, gs):
    gs.status = "finished"
    gs.mission_phase = "finished"
    gs.mission_locked = True
    ended_at = time.time()

    async with get_db() as db:
        await db.execute(
            "UPDATE games SET status='finished', ended_at=?, time_remaining=0 WHERE code=?",
            (ended_at, code)
        )
        await db.commit()

    recalculate_ranks(code)
    leaderboard = [vars(p) for p in get_leaderboard(code)]

    await publish_to_ably(f"game:{code}", "game_ended", {"leaderboard": leaderboard})
    return {"success": True, "game_ended": True, "leaderboard": leaderboard}


# ── PAUSAR / RESUMIR ─────────────────────────────────────────────────────────
@router.post("/{code}/pause")
async def pause_game(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    if gs.status == "active":
        gs.status = "paused"
        event = "game_paused"
    elif gs.status == "paused":
        gs.status = "active"
        event = "game_resumed"
    else:
        raise HTTPException(400, "Cannot pause/resume in current status")

    async with get_db() as db:
        await db.execute("UPDATE games SET status=? WHERE code=?", (gs.status, code))
        await db.commit()

    await publish_to_ably(f"game:{code}", event, {})
    return {"status": gs.status}


# ── TERMINAR PARTIDA ─────────────────────────────────────────────────────────
@router.post("/{code}/end")
async def end_game(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    return await _finish_game(code, gs)


# ── ROUND STATUS (para admin en tiempo real) ──────────────────────────────────
@router.get("/{code}/round/status")
async def get_round_status_endpoint(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    return get_round_status(code)

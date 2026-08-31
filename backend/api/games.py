import random
import time
import uuid
import json
from fastapi import APIRouter, HTTPException, Depends
from backend.models.game import CreateGameRequest, JoinGameRequest, GameResponse, StartGameRequest
from backend.core.matchmaking import generate_game_code, generate_player_id
from backend.core.security import create_admin_token, create_player_token, get_admin
from backend.core.database import get_db
from backend.core.game_state import create_game, get_game, set_status, add_player, PlayerState
from backend.app import publish_to_ably

router = APIRouter(prefix="/api/games", tags=["games"])

@router.post("/create")
async def create_new_game(req: CreateGameRequest):
    game_code   = generate_game_code()
    admin_token = create_admin_token()

    # Solo dos premios reales: agua y pelota
    prizes = [
        {"name": "Botella de agua", "emoji": "💧", "stock": req.max_players or 5},
        {"name": "Pelota",          "emoji": "⚽", "stock": req.max_players or 5},
    ]

    # Forzar máximo 5 jugadores
    max_pl = min(req.max_players or 5, 5)

    async with get_db() as db:
        await db.execute(
            """INSERT INTO games (id, code, name, difficulty, max_players, duration_seconds, rounds, prizes_config, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), game_code, req.name, req.difficulty, max_pl,
             req.duration_seconds, req.rounds, json.dumps(prizes), time.time())
        )
        await db.commit()

    create_game(game_code, {**req.dict(), "max_players": max_pl})
    return {"game_code": game_code, "admin_token": admin_token}

@router.post("/join")
async def join_game(req: JoinGameRequest):
    gs = get_game(req.game_code)
    if not gs or gs.status != "waiting":
        raise HTTPException(400, "Game not found or not waiting")
    if len(gs.players) >= gs.max_players:
        raise HTTPException(400, "Game is full")
    
    for p in gs.players.values():
        if p.name == req.player_name:
            raise HTTPException(400, "Name already taken in this game")

    player_id = generate_player_id()
    colors = ["#FF5733", "#33FF57", "#3357FF", "#F1C40F", "#9B59B6", "#1ABC9C", "#E67E22", "#E74C3C", "#34495E", "#2ECC71", "#3498DB", "#95A5A6"]
    avatar_color = random.choice(colors)
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

@router.get("/{code}/state")
async def get_game_state_endpoint(code: str):
    gs = get_game(code)
    if not gs:
        raise HTTPException(404, "Game not found")
    # ── Tiempo restante REAL calculado desde el inicio (consistente entre dispositivos) ──
    remaining = gs.time_remaining
    if gs.status == "active" and gs.started_at:
        remaining = max(0, int(round(gs.duration_seconds - (time.time() - gs.started_at))))
        gs.time_remaining = remaining
        if remaining <= 0:
            gs.status = "finished"
    players = [vars(p) for p in gs.players.values()]
    return {
        "game_code":    code,
        "status":       gs.status,
        "difficulty":   gs.difficulty,
        "total_rounds": gs.total_rounds,
        "current_round": gs.current_round,
        "max_players":  gs.max_players,
        "duration_seconds": gs.duration_seconds,
        "time_remaining":   remaining,
        "players":      players,
    }

@router.post("/{code}/start")
async def start_game(code: str, admin=Depends(get_admin)):
    gs = get_game(code)
    if not gs or gs.status != "waiting":
        raise HTTPException(400, "Cannot start this game")
    
    gs.status = "active"
    gs.started_at = time.time()
    gs.time_remaining = gs.duration_seconds
    
    async with get_db() as db:
        await db.execute("UPDATE games SET status = 'active', started_at = ?, time_remaining = ? WHERE code = ?", (gs.started_at, gs.time_remaining, code))
        await db.commit()
        
    await publish_to_ably(f"game:{code}", "countdown_start", {"duration": gs.duration_seconds})
    await publish_to_ably(f"game:{code}", "game_started", {"game_code": code})
    return {"success": True}

@router.post("/{code}/pause")
async def pause_game(code: str, admin=Depends(get_admin)):
    gs = get_game(code)
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
        await db.execute("UPDATE games SET status = ? WHERE code = ?", (gs.status, code))
        await db.commit()
    
    await publish_to_ably(f"game:{code}", event, {})
    return {"status": gs.status}

@router.post("/{code}/end")
async def end_game(code: str, admin=Depends(get_admin)):
    gs = get_game(code)
    if not gs:
        raise HTTPException(404, "Game not found")
        
    gs.status = "finished"
    gs.time_remaining = 0
    ended_at = time.time()
    
    async with get_db() as db:
        await db.execute("UPDATE games SET status = 'finished', ended_at = ?, time_remaining = 0 WHERE code = ?", (ended_at, code))
        await db.commit()
        
    from backend.core.game_state import recalculate_ranks, get_leaderboard
    recalculate_ranks(code)
    leaderboard = [vars(p) for p in get_leaderboard(code)]
    
    await publish_to_ably(f"game:{code}", "game_ended", {"leaderboard": leaderboard})
    return {"leaderboard": leaderboard}

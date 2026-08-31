from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time

@dataclass
class PlayerState:
    player_id: str
    name: str
    avatar_color: str
    avatar_initials: str
    points: int = 0
    streak: int = 0
    max_streak: int = 0
    rank: Optional[int] = None
    missions_completed: int = 0
    missions_failed: int = 0
    current_mission_type: Optional[str] = None
    status: str = "connected"
    last_action_at: float = field(default_factory=time.time)

@dataclass
class GameState:
    game_code: str
    name: str
    status: str = "waiting"
    difficulty: str = "normal"
    players: Dict[str, PlayerState] = field(default_factory=dict)
    current_round: int = 0
    total_rounds: int = 5
    time_remaining: Optional[int] = None
    started_at: Optional[float] = None
    duration_seconds: int = 480
    active_global_events: list = field(default_factory=list)
    max_players: int = 20

_games: Dict[str, GameState] = {}

def get_game(code: str) -> Optional[GameState]:
    return _games.get(code)

def create_game(code: str, config: dict) -> GameState:
    gs = GameState(
        game_code=code,
        name=config.get("name", "New Game"),
        difficulty=config.get("difficulty", "normal"),
        duration_seconds=config.get("duration_seconds", 480),
        total_rounds=config.get("rounds", 5),
        max_players=config.get("max_players", 20)
    )
    _games[code] = gs
    return gs

def add_player(code: str, player: PlayerState) -> bool:
    gs = get_game(code)
    if not gs or len(gs.players) >= gs.max_players:
        return False
    gs.players[player.player_id] = player
    return True

def remove_player(code: str, player_id: str):
    gs = get_game(code)
    if gs and player_id in gs.players:
        del gs.players[player_id]

def update_score(code: str, player_id: str, points_delta: int, mission_result: bool):
    gs = get_game(code)
    if gs and player_id in gs.players:
        p = gs.players[player_id]
        p.points += points_delta
        if mission_result:
            p.missions_completed += 1
            p.streak += 1
            p.max_streak = max(p.streak, p.max_streak)
        else:
            p.missions_failed += 1
            p.streak = 0
        recalculate_ranks(code)

def recalculate_ranks(code: str):
    gs = get_game(code)
    if not gs:
        return
    sorted_players = sorted(gs.players.values(), key=lambda p: (-p.points, p.last_action_at))
    for idx, p in enumerate(sorted_players, start=1):
        p.rank = idx

def get_leaderboard(code: str) -> List[PlayerState]:
    gs = get_game(code)
    if not gs:
        return []
    return sorted(gs.players.values(), key=lambda p: (-p.points, p.last_action_at))

def set_status(code: str, status: str):
    gs = get_game(code)
    if gs:
        gs.status = status

def tick(code: str) -> Optional[int]:
    gs = get_game(code)
    if gs and gs.status == "active" and gs.time_remaining is not None:
        if gs.time_remaining > 0:
            gs.time_remaining -= 1
        return gs.time_remaining
    return None

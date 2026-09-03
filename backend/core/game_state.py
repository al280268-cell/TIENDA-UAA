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
    # Per-round tracking
    round_answered: bool = False      # Did player answer current round?
    round_correct: Optional[bool] = None
    round_points: int = 0
    round_answer_ts: Optional[float] = None  # When they answered (for tiebreak)

@dataclass
class GameState:
    game_code: str
    name: str
    status: str = "waiting"           # waiting | active | finished
    difficulty: str = "normal"
    players: Dict[str, PlayerState] = field(default_factory=dict)
    current_round: int = 0
    total_rounds: int = 5
    time_remaining: Optional[int] = None
    started_at: Optional[float] = None
    duration_seconds: int = 480
    active_global_events: list = field(default_factory=list)
    max_players: int = 20

    # ── Kahoot-style mission sync ──────────────────────────────────────────
    current_mission_index: int = -1          # -1 = lobby / not started
    missions_order: List[str] = field(default_factory=list)
    mission_start_ts: Optional[float] = None
    mission_duration_sec: int = 30           # seconds per question/mission
    mission_locked: bool = False
    mission_locked_at: Optional[float] = None  # when was it locked (for auto-advance)
    mission_phase: str = "lobby"             # lobby|active|locked|results|store_simulation|finished
    results_display_sec: int = 5             # seconds to show results before next mission

    # ── Store simulation phase (all players go at same time, wait for everyone) ─
    store_done_players: set = field(default_factory=set)   # player_ids who finished the store
    store_simulation_started_at: Optional[float] = None    # timestamp when sim phase began (for timeout)


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
        max_players=config.get("max_players", 20),
        mission_duration_sec=config.get("mission_duration_sec", 60),
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
    # Primary: points desc. Tiebreak: faster answer time (lower round_answer_ts wins)
    sorted_players = sorted(
        gs.players.values(),
        key=lambda p: (-p.points, p.round_answer_ts or float('inf'), p.last_action_at)
    )
    for idx, p in enumerate(sorted_players, start=1):
        p.rank = idx

def get_leaderboard(code: str) -> List[PlayerState]:
    gs = get_game(code)
    if not gs:
        return []
    return sorted(
        gs.players.values(),
        key=lambda p: (-p.points, p.round_answer_ts or float('inf'), p.last_action_at)
    )

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

# ── Kahoot round helpers ─────────────────────────────────────────────────────

def start_mission_round(code: str, mission_index: int, mission_id: str) -> bool:
    """Start a new synchronized mission round. Returns True on success."""
    gs = get_game(code)
    if not gs:
        return False
    # Reset per-round player state
    for p in gs.players.values():
        p.round_answered = False
        p.round_correct = None
        p.round_points = 0
        p.round_answer_ts = None
    gs.current_mission_index = mission_index
    gs.mission_start_ts = time.time()
    gs.mission_locked = False
    gs.mission_phase = "active"
    return True

def lock_mission_round(code: str) -> dict:
    """Lock the current mission round (time up). Returns round summary."""
    gs = get_game(code)
    if not gs:
        return {}
    gs.mission_locked = True
    gs.mission_locked_at = time.time()
    gs.mission_phase = "locked"
    recalculate_ranks(code)

    results = []
    for p in gs.players.values():
        results.append({
            "player_id": p.player_id,
            "name": p.name,
            "avatar_color": p.avatar_color,
            "avatar_initials": p.avatar_initials,
            "answered": p.round_answered,
            "correct": p.round_correct,
            "points_earned": p.round_points,
            "total_points": p.points,
            "rank": p.rank,
        })
    return {"results": results}

def record_round_answer(code: str, player_id: str, correct: bool, points: int) -> bool:
    """Record a player's answer for the current round. Returns False if locked."""
    gs = get_game(code)
    if not gs or gs.mission_locked:
        return False
    p = gs.players.get(player_id)
    if not p:
        return False
    if p.round_answered:
        return True  # Already answered, ignore duplicate
    p.round_answered = True
    p.round_correct = correct
    p.round_points = points
    p.round_answer_ts = time.time()
    return True

def get_mission_time_remaining(code: str) -> int:
    """Returns seconds remaining in current mission round (authoritative)."""
    gs = get_game(code)
    if not gs or gs.mission_start_ts is None or gs.mission_locked:
        return 0
    elapsed = time.time() - gs.mission_start_ts
    remaining = int(gs.mission_duration_sec - elapsed)
    return max(0, remaining)

def get_round_status(code: str) -> dict:
    """Returns current round status for admin panel."""
    gs = get_game(code)
    if not gs:
        return {}
    answered = sum(1 for p in gs.players.values() if p.round_answered)
    total = len(gs.players)
    return {
        "mission_index": gs.current_mission_index,
        "mission_phase": gs.mission_phase,
        "mission_locked": gs.mission_locked,
        "time_remaining": get_mission_time_remaining(code),
        "answered": answered,
        "total_players": total,
        "player_statuses": [
            {
                "player_id": p.player_id,
                "name": p.name,
                "avatar_color": p.avatar_color,
                "avatar_initials": p.avatar_initials,
                "answered": p.round_answered,
                "correct": p.round_correct,
                "points": p.points,
                "rank": p.rank,
            }
            for p in gs.players.values()
        ]
    }

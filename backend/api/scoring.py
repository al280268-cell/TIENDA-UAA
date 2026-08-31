from fastapi import APIRouter
from backend.models.game import ScoreSubmitRequest
from backend.core.game_state import get_leaderboard, get_game

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

# Base points per mission type
BASE_POINTS = {
    "detective": 80,
    "find_error": 90,
    "best_cart": 100,
    "decision": 70,
    "speed": 100,
    "memory": 80,
    "order": 70,
    "code": 120,
    "social": 150,
    "special": 200,
}

# Minimum time thresholds (ms) — faster than these is suspicious
MIN_MISSION_TIMES = {
    "speed": 2000,
    "memory": 3000,
    "detective": 5000,
    "find_error": 5000,
    "best_cart": 8000,
    "order": 5000,
    "default": 3000,
}

# Difficulty multipliers
DIFFICULTY_MULTIPLIERS = {
    "easy": 0.8,
    "normal": 1.0,
    "hard": 1.3,
    "feria": 1.5,
}


def calculate_points(
    mission_type: str,
    is_correct: bool,
    time_taken_ms: int,
    player_id: str,
    game_code: str,
) -> tuple[int, int]:
    """
    Scoring formula:
    Points = base × difficulty × precision_bonus + speed_bonus + special_bonus × streak_multiplier
    Penalty: wrong answer = -20 pts
    """
    gs = get_game(game_code)
    difficulty = gs.difficulty if gs else "normal"
    player = gs.players.get(player_id) if gs else None
    streak = player.streak if player else 0

    # ── Base points ──────────────────────────────────────────────────────────
    base = BASE_POINTS.get(mission_type, 50)

    if not is_correct:
        penalty = 20
        return 0, penalty

    # ── Difficulty multiplier ─────────────────────────────────────────────────
    diff_mult = DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
    points = int(base * diff_mult)

    # ── Precision bonus (no failed attempts counted on this call) ─────────────
    # We award precision bonus since the answer just came in as correct.
    # A previous wrong attempt is already recorded as penalty elsewhere.
    precision_bonus = 30

    # ── Speed bonus ───────────────────────────────────────────────────────────
    speed_bonus = 0
    if mission_type == "speed":
        time_limit_ms = 20_000  # 20s default speed limit
        ratio = time_taken_ms / time_limit_ms if time_limit_ms else 1
        if ratio < 0.30:
            speed_bonus = 50
        elif ratio < 0.60:
            speed_bonus = 25
    else:
        # For non-speed missions: reward quick thinking too
        if time_taken_ms < 8_000:
            speed_bonus = 20
        elif time_taken_ms < 15_000:
            speed_bonus = 10

    # ── Streak multiplier ─────────────────────────────────────────────────────
    if streak >= 4:
        streak_mult = 2.0
    elif streak == 3:
        streak_mult = 1.5
    elif streak == 2:
        streak_mult = 1.25
    else:
        streak_mult = 1.0

    # ── Special mission extra bonus ───────────────────────────────────────────
    special_bonus = 150 if mission_type == "special" else 0

    # ── Final calculation ─────────────────────────────────────────────────────
    total = int((points + precision_bonus + speed_bonus + special_bonus) * streak_mult)
    return max(total, 1), 0  # always at least 1 point for a correct answer


@router.post("/submit")
async def submit_score(req: ScoreSubmitRequest):
    """Generic score submission endpoint (supplementary to mission validate)."""
    return {"success": True}


@router.get("/leaderboard/{code}")
async def get_game_leaderboard(code: str):
    """Returns the current sorted leaderboard for a game."""
    lb = get_leaderboard(code)
    return [
        {
            "player_id": p.player_id,
            "name": p.name,
            "avatar_color": p.avatar_color,
            "avatar_initials": p.avatar_initials,
            "points": p.points,
            "streak": p.streak,
            "max_streak": p.max_streak,
            "rank": p.rank,
            "missions_completed": p.missions_completed,
            "missions_failed": p.missions_failed,
            "status": p.status,
        }
        for p in lb
    ]

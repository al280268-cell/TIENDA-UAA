from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CreateGameRequest(BaseModel):
    name: str = "New Game"
    difficulty: str = "normal"
    max_players: int = 20
    duration_seconds: int = 180
    rounds: int = 5
    prizes_config: List[Dict[str, Any]] = []

class JoinGameRequest(BaseModel):
    game_code: str
    player_name: str

class GameResponse(BaseModel):
    code: str
    name: str
    status: str
    difficulty: str
    current_round: int
    total_rounds: int
    time_remaining: Optional[int]
    player_count: int
    max_players: int

class PlayerResponse(BaseModel):
    player_id: str
    name: str
    avatar_color: str
    avatar_initials: str
    points: int
    streak: int
    rank: Optional[int]
    status: str

class LeaderboardEntry(BaseModel):
    rank: int
    player_id: str
    name: str
    avatar_color: str
    avatar_initials: str
    points: int
    streak: int
    missions_completed: int
    status: str

class MissionValidateRequest(BaseModel):
    player_id: str
    game_code: str
    mission_id: str
    mission_type: str
    answer: Any
    time_taken_ms: int

class MissionValidateResponse(BaseModel):
    correct: bool
    points: int
    penalty: int
    total_points: int
    streak: int
    explanation: str
    new_rank: Optional[int]

class ScoreSubmitRequest(BaseModel):
    player_id: str
    game_code: str
    action_type: str
    action_data: Dict[str, Any]

class StartGameRequest(BaseModel):
    game_code: str

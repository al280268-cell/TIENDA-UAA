from pydantic import BaseModel
from typing import Optional

class RewardResponse(BaseModel):
    id: str
    name: str
    emoji: str
    stock_remaining: int
    min_points: int
    min_rank: Optional[int]

class ClaimRewardRequest(BaseModel):
    player_id: str
    game_code: str
    reward_id: str

class ClaimRewardResponse(BaseModel):
    success: bool
    claim_code: str
    message: str

class CreateCodeRequest(BaseModel):
    code: str
    reward_points: int
    mission_type: Optional[str]
    max_uses: int
    expires_in_minutes: int
    game_code: Optional[str]

class ValidateCodeRequest(BaseModel):
    player_id: str
    game_code: str
    code: str

class ValidateCodeResponse(BaseModel):
    valid: bool
    points: int
    message: str

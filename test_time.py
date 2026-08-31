import asyncio
from backend.core.game_state import games, GameState

games["TEST"] = GameState(id="1", code="TEST", name="Test", difficulty="easy", max_players=10, duration_seconds=600, rounds=1, prizes_config="[]", created_at=0)
print(games["TEST"].time_remaining)

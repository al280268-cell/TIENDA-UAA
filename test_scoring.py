import asyncio
from backend.core.game_state import update_score, games, GameState, PlayerState

games["TESTGAME"] = GameState(id="1", code="TESTGAME", name="Test", difficulty="easy", max_players=10, duration_seconds=600, rounds=1, prizes_config="[]", created_at=0)
games["TESTGAME"].players["TESTPLAYER"] = PlayerState(player_id="TESTPLAYER", name="Test", avatar_color="#000", avatar_initials="T", joined_at=0)

print(games["TESTGAME"].players["TESTPLAYER"].points)
update_score("TESTGAME", "TESTPLAYER", 100, True)
print(games["TESTGAME"].players["TESTPLAYER"].points)

try:
    from backend.app import publish_to_ably
    print("publish_to_ably imported!")
except Exception as e:
    print("Error importing publish_to_ably:", e)

import time
import json
import uuid

class AntiCheatMonitor:
    def __init__(self):
        self.player_actions = {}

    def check_rate_limit(self, player_id: str, max_per_second: int = 3) -> bool:
        now = time.time()
        if player_id not in self.player_actions:
            self.player_actions[player_id] = []
        
        self.player_actions[player_id].append(now)
        # Keep only last 1 second of actions
        self.player_actions[player_id] = [t for t in self.player_actions[player_id] if now - t <= 1.0]
        
        return len(self.player_actions[player_id]) > max_per_second

    def check_mission_time(self, time_ms: int, mission_type: str) -> bool:
        minimum_times = {
            "speed": 2000,
            "memory": 3000,
            "detective": 5000
        }
        min_time = minimum_times.get(mission_type, 3000)
        return time_ms < min_time

    def record_action(self, player_id: str, action_type: str):
        pass # Optional tracking logic

    def get_suspicious_players(self, game_code: str) -> list[str]:
        return []

    async def log_suspicious(self, db, player_id: str, game_code: str, details: dict):
        action_json = json.dumps(details)
        await db.execute(
            "INSERT INTO audit_logs (id, player_id, game_code, action, details, is_suspicious, created_at) VALUES (?, ?, ?, ?, ?, 1, ?)",
            (str(uuid.uuid4()), player_id, game_code, "suspicious_activity", action_json, time.time())
        )
        await db.commit()

anti_cheat = AntiCheatMonitor()

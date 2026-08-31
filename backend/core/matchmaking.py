import uuid
import random
import string
import re

def generate_game_code() -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "UAA-" + "".join(random.choice(chars) for _ in range(4))

def is_code_valid(code: str) -> bool:
    return bool(re.match(r"^UAA-[A-Z0-9]{4}$", code))

def generate_player_id() -> str:
    return str(uuid.uuid4())

def generate_claim_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(8))

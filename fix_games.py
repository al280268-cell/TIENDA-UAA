with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix join endpoint
text = text.replace(
    """@router.post("/join")
async def join_game(req: JoinGameRequest):
    gs = get_game(req.game_code)
    if not gs or gs.status != "waiting":""",
    """@router.post("/join")
async def join_game(req: JoinGameRequest):
    gs = await _ensure_in_memory(req.game_code)
    if not gs or gs.status not in ("waiting", "active"):"""
)

# Fix state endpoint
text = text.replace(
    """@router.get("/{code}/state")
async def get_game_state_endpoint(code: str):
    gs = get_game(code)""",
    """@router.get("/{code}/state")
async def get_game_state_endpoint(code: str):
    gs = await _ensure_in_memory(code)"""
)

# Fix start endpoint - allow restart of active games too
text = text.replace(
    """@router.post("/{code}/start")
async def start_game(code: str, admin=Depends(get_admin)):
    gs = get_game(code)
    if not gs or gs.status != "waiting":
        raise HTTPException(400, "Cannot start this game")""",
    """@router.post("/{code}/start")
async def start_game(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)
    if not gs:
        raise HTTPException(404, "Game not found in DB")
    if gs.status == "finished":
        raise HTTPException(400, "Game already finished")"""
)

# Fix mission/start endpoint
text = text.replace(
    """async def admin_start_mission(code: str, req: MissionStartRequest, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """async def admin_start_mission(code: str, req: MissionStartRequest, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)"""
)

# Fix missions/order endpoint
text = text.replace(
    """async def set_missions_order(code: str, req: SetMissionsOrderRequest, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """async def set_missions_order(code: str, req: SetMissionsOrderRequest, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)"""
)

# Fix mission/lock endpoint
text = text.replace(
    """async def admin_lock_mission(code: str, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """async def admin_lock_mission(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)"""
)

# Fix mission/next endpoint
text = text.replace(
    """async def admin_next_mission(code: str, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """async def admin_next_mission(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)"""
)

# Fix pause endpoint
text = text.replace(
    """async def pause_game(code: str, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """async def pause_game(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)"""
)

# Fix end endpoint
text = text.replace(
    """async def end_game(code: str, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """async def end_game(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)"""
)

# Fix round/status endpoint
text = text.replace(
    """async def get_round_status_endpoint(code: str, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """async def get_round_status_endpoint(code: str, admin=Depends(get_admin)):
    gs = await _ensure_in_memory(code)"""
)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\games.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Done. Replacements applied.")

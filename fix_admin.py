with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\admin.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix get_game_detail endpoint
text = text.replace(
    """@router.get("/game/{code}")
async def get_game_detail(code: str, admin=Depends(get_admin)):
    gs = get_game(code)""",
    """@router.get("/game/{code}")
async def get_game_detail(code: str, admin=Depends(get_admin)):
    from backend.api.games import _ensure_in_memory
    gs = await _ensure_in_memory(code)"""
)

# Fix live endpoint
text = text.replace(
    """@router.get("/game/{code}/live")
async def get_live_status(code: str, admin=Depends(get_admin)):
    \"\"\"Full real-time status for the admin control panel.\"\"\"
    gs = get_game(code)""",
    """@router.get("/game/{code}/live")
async def get_live_status(code: str, admin=Depends(get_admin)):
    \"\"\"Full real-time status for the admin control panel.\"\"\"
    from backend.api.games import _ensure_in_memory
    gs = await _ensure_in_memory(code)"""
)

# Fix kick endpoint
text = text.replace(
    """async def kick_player(req: KickPlayerRequest, admin=Depends(get_admin)):
    remove_player(req.game_code, req.player_id)""",
    """async def kick_player(req: KickPlayerRequest, admin=Depends(get_admin)):
    from backend.api.games import _ensure_in_memory
    await _ensure_in_memory(req.game_code)
    remove_player(req.game_code, req.player_id)"""
)

# Fix add_time endpoint
text = text.replace(
    """async def add_time(req: AddTimeRequest, admin=Depends(get_admin)):
    gs = get_game(req.game_code)""",
    """async def add_time(req: AddTimeRequest, admin=Depends(get_admin)):
    from backend.api.games import _ensure_in_memory
    gs = await _ensure_in_memory(req.game_code)"""
)

with open(r"c:\Users\PC\Downloads\TIENDA_UAA_v9\TIENDA UAA\backend\api\admin.py", "w", encoding="utf-8") as f:
    f.write(text)

print("admin.py patched OK")

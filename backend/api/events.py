import uuid
import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.core.security import get_admin
from backend.core.database import get_db
from backend.app import publish_to_ably

router = APIRouter(prefix="/api/events", tags=["events"])

class GlobalEventRequest(BaseModel):
    game_code: str
    event_type: str
    event_data: dict

@router.post("/global")
async def trigger_global_event(req: GlobalEventRequest, admin=Depends(get_admin)):
    async with get_db() as db:
        import json
        await db.execute(
            """INSERT INTO events (id, game_code, event_type, event_data, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), req.game_code, req.event_type, json.dumps(req.event_data), time.time())
        )
        await db.commit()
        
    await publish_to_ably(f"game:{req.game_code}", req.event_type, req.event_data)
    return {"success": True}

@router.get("/{code}")
async def get_events(code: str):
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM events WHERE game_code = ? ORDER BY created_at DESC LIMIT 10", (code,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

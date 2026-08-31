import asyncio
from backend.api.missions import get_pool
from backend.core.database import init_db

async def test():
    await init_db()
    res = await get_pool("UAA-2BR3", "TEST-PLAYER-ID")
    print(res)

asyncio.run(test())

import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_code: str):
        await websocket.accept()
        if game_code not in self.active_connections:
            self.active_connections[game_code] = set()
        self.active_connections[game_code].add(websocket)

    def disconnect(self, websocket: WebSocket, game_code: str):
        if game_code in self.active_connections:
            self.active_connections[game_code].discard(websocket)
            if not self.active_connections[game_code]:
                del self.active_connections[game_code]

    async def broadcast(self, game_code: str, message: dict):
        if game_code in self.active_connections:
            websockets = self.active_connections[game_code].copy()
            for connection in websockets:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    self.disconnect(connection, game_code)

manager = ConnectionManager()

@app.websocket("/ws/{game_code}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_code: str, player_id: str):
    await manager.connect(websocket, game_code)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed, then broadcast
            await manager.broadcast(game_code, {"event": "player_action", "data": json.loads(data)})
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_code)
        await manager.broadcast(game_code, {"event": "player_disconnected", "data": {"player_id": player_id}})

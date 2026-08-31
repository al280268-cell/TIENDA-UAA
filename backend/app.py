from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
import base64
import os

from backend.core.config import settings
from backend.core.database import init_db

app = FastAPI(
    title="Feria UAA — Reto E-Commerce",
    version="1.0.0",
    description="Backend multijugador para la Feria Universitaria UAA"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def publish_to_ably(channel: str, event: str, data: dict):
    """Publish a message to an Ably channel via REST API.
    Falls back to console log when ABLY_API_KEY is not configured (local dev).
    """
    # Una API key real de Ably tiene el formato "xxxxx.yyyyy:zzzzz".
    # Si está vacía o es un placeholder del .env.example, usamos modo DEV
    # (el frontend cae a polling) en vez de spamear 403 contra rest.ably.io.
    key = (settings.ABLY_API_KEY or "").strip()
    if not key or ":" not in key or key.startswith("tu_"):
        print(f"[Ably DEV] ch={channel} ev={event} data={data}")
        return

    url = f"https://rest.ably.io/channels/{channel}/messages"
    auth_header = "Basic " + base64.b64encode(settings.ABLY_API_KEY.encode()).decode()
    payload = {"name": event, "data": data}

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(url, json=payload, headers={"Authorization": auth_header})
            if resp.status_code >= 400:
                print(f"[Ably ERROR] {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"[Ably EXCEPTION] {e}")


# Import routers AFTER defining publish_to_ably to avoid circular imports
from backend.api import games, players, missions, scoring, rewards, codes, events, admin, quiz  # noqa: E402

app.include_router(games.router)
app.include_router(players.router)
app.include_router(missions.router)
app.include_router(scoring.router)
app.include_router(rewards.router)
app.include_router(codes.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(quiz.router)


@app.on_event("startup")
async def startup_event():
    await init_db()
    print("Database initialized OK")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


# ── Servir frontend estático ─────────────────────────────────────
# IMPORTANTE: esto debe ir AL FINAL, después de todos los routers API
# para que /api/* sea atendido por los routers y no por StaticFiles.
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
_frontend_dir = os.path.abspath(_frontend_dir)

if os.path.isdir(_frontend_dir):
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(_frontend_dir, "index.html"))

    @app.get("/admin")
    async def serve_admin():
        return FileResponse(os.path.join(_frontend_dir, "admin.html"))

    # Archivos estáticos (CSS, JS, imágenes, etc.)
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

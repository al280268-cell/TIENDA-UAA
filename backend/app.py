from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
import base64
import os
import asyncio
import time as _time

from backend.core.config import settings
from backend.core.database import init_db

app = FastAPI(
    title="Feria UAA – Reto E-Commerce",
    version="2.0.0",
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
    key = (settings.ABLY_API_KEY or "").strip()
    if not key or ":" not in key or key.startswith("tu_"):
        print(f"[Ably DEV] ch={channel} ev={event} data={str(data)[:120]}")
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


# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND TIMER — Fully automatic Kahoot-style flow
#
# State machine:
#   active  →  (timer hits 0)  →  locked  →  (5s results)  →  active (next)
#                                                           →  finished (last)
# ─────────────────────────────────────────────────────────────────────────────
async def _mission_timer_loop():
    """Runs every second. Drives the automatic mission progression."""
    await asyncio.sleep(3)  # Let app fully start
    while True:
        try:
            from backend.core.game_state import (
                _games, lock_mission_round, get_leaderboard,
                get_mission_time_remaining, start_mission_round
            )
            now = _time.time()

            for code, gs in list(_games.items()):

                # ── Phase: ACTIVE → check if time is up ──────────────────────
                if gs.mission_phase == "active" and not gs.mission_locked:
                    remaining = get_mission_time_remaining(code)
                    if remaining <= 0:
                        summary   = lock_mission_round(code)
                        leaderboard = [vars(p) for p in get_leaderboard(code)]
                        print(f"[Kahoot] Mission {gs.current_mission_index} LOCKED for game {code}")
                        await publish_to_ably(f"game:{code}", "mission_locked", {
                            "mission_index": gs.current_mission_index,
                            "results":       summary.get("results", []),
                            "leaderboard":   leaderboard,
                        })

                # ── Phase: LOCKED → wait results_display_sec then auto-advance ──
                elif gs.mission_phase == "locked" and gs.mission_locked_at is not None:
                    waited = now - gs.mission_locked_at
                    if waited >= gs.results_display_sec:
                        next_index = gs.current_mission_index + 1

                        if next_index < len(gs.missions_order):
                            # Auto-advance to next mission
                            mission_id = gs.missions_order[next_index]
                            start_mission_round(code, next_index, mission_id)
                            leaderboard = [vars(p) for p in get_leaderboard(code)]
                            print(f"[Kahoot] Auto-starting mission {next_index} for game {code}")
                            await publish_to_ably(f"game:{code}", "mission_started", {
                                "mission_index":  next_index,
                                "mission_id":     mission_id,
                                "duration_sec":   gs.mission_duration_sec,
                                "start_ts":       gs.mission_start_ts,
                                "total_missions": len(gs.missions_order),
                                "leaderboard":    leaderboard,
                            })
                        else:
                            # All quiz missions done — enter store simulation phase
                            # All players go to store at the same time; wait for all to finish
                            gs.mission_phase = "store_simulation"
                            gs.store_simulation_started_at = now
                            gs.store_done_players = set()
                            gs.mission_locked = True
                            recalc_needed = True
                            from backend.core.game_state import recalculate_ranks
                            recalculate_ranks(code)
                            leaderboard = [vars(p) for p in get_leaderboard(code)]
                            print(f"[Kahoot] Game {code} → STORE SIMULATION phase")
                            await publish_to_ably(f"game:{code}", "store_simulation_started", {
                                "leaderboard": leaderboard
                            })

                # ── Phase: STORE_SIMULATION → wait for all players or timeout ──
                elif gs.mission_phase == "store_simulation" and gs.store_simulation_started_at is not None:
                    total_players = len(gs.players)
                    done_count    = len(gs.store_done_players)
                    elapsed       = now - gs.store_simulation_started_at
                    STORE_TIMEOUT = 120  # seconds — give up waiting after 2 minutes

                    all_done   = total_players > 0 and done_count >= total_players
                    timed_out  = elapsed >= STORE_TIMEOUT

                    if all_done or timed_out:
                        gs.status        = "finished"
                        gs.mission_phase = "finished"
                        from backend.core.game_state import recalculate_ranks
                        recalculate_ranks(code)
                        leaderboard = [vars(p) for p in get_leaderboard(code)]
                        reason = "all_done" if all_done else "timeout"
                        print(f"[Kahoot] Game {code} FINISHED (store phase {reason})")
                        await publish_to_ably(f"game:{code}", "game_ended", {
                            "leaderboard": leaderboard,
                            "reason": reason
                        })
                        # Persist to DB
                        try:
                            from backend.core.database import get_db
                            async with get_db() as db:
                                await db.execute(
                                    "UPDATE games SET status='finished', ended_at=? WHERE code=?",
                                    (_time.time(), code)
                                )
                                await db.commit()
                        except Exception as e:
                            print(f"[Timer DB] {e}")

        except Exception as e:
            print(f"[Timer ERROR] {e}")

        await asyncio.sleep(1)


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
    asyncio.create_task(_mission_timer_loop())
    print("Kahoot auto-timer started")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}


# Servir frontend estático — MUST be at the end, after all API routers
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
_frontend_dir = os.path.abspath(_frontend_dir)

if os.path.isdir(_frontend_dir):
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(_frontend_dir, "index.html"))

    @app.get("/admin")
    async def serve_admin():
        return FileResponse(os.path.join(_frontend_dir, "admin.html"))

    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

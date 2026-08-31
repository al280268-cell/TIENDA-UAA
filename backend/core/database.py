import aiosqlite
from contextlib import asynccontextmanager

db_path = "./game.db"

@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    async with get_db() as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS games (
          id TEXT PRIMARY KEY,
          code TEXT UNIQUE NOT NULL,
          name TEXT,
          status TEXT DEFAULT 'waiting',
          difficulty TEXT DEFAULT 'normal',
          max_players INTEGER DEFAULT 20,
          duration_seconds INTEGER DEFAULT 480,
          rounds INTEGER DEFAULT 5,
          current_round INTEGER DEFAULT 0,
          time_remaining INTEGER,
          prizes_config TEXT,
          created_at REAL,
          started_at REAL,
          ended_at REAL
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS players (
          id TEXT PRIMARY KEY,
          game_code TEXT,
          name TEXT,
          avatar_color TEXT,
          avatar_initials TEXT,
          status TEXT DEFAULT 'connected',
          is_suspicious INTEGER DEFAULT 0,
          joined_at REAL,
          finished_at REAL
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS player_missions (
          id TEXT PRIMARY KEY,
          player_id TEXT,
          game_code TEXT,
          round_number INTEGER,
          mission_type TEXT,
          mission_data TEXT,
          answer_submitted TEXT,
          is_correct INTEGER,
          points_earned INTEGER DEFAULT 0,
          time_taken_ms INTEGER,
          attempts INTEGER DEFAULT 0,
          completed_at REAL,
          status TEXT DEFAULT 'available',
          started_at REAL
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS quiz_progress (
          game_code TEXT,
          player_id TEXT,
          mission_id TEXT,
          status TEXT DEFAULT 'available',
          run_data TEXT,
          started_at REAL,
          PRIMARY KEY (game_code, player_id, mission_id)
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
          key TEXT PRIMARY KEY,
          value TEXT
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS scores (
          id TEXT PRIMARY KEY,
          player_id TEXT,
          game_code TEXT,
          total_points INTEGER DEFAULT 0,
          base_points INTEGER DEFAULT 0,
          bonus_points INTEGER DEFAULT 0,
          penalties INTEGER DEFAULT 0,
          missions_completed INTEGER DEFAULT 0,
          missions_failed INTEGER DEFAULT 0,
          streak INTEGER DEFAULT 0,
          max_streak INTEGER DEFAULT 0,
          rank INTEGER,
          updated_at REAL
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS rewards (
          id TEXT PRIMARY KEY,
          name TEXT,
          emoji TEXT,
          stock_initial INTEGER DEFAULT 0,
          stock_remaining INTEGER DEFAULT 0,
          min_points INTEGER DEFAULT 0,
          min_rank INTEGER,
          game_code TEXT
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS redemptions (
          id TEXT PRIMARY KEY,
          player_id TEXT,
          reward_id TEXT,
          game_code TEXT,
          claim_code TEXT,
          claimed_at REAL,
          delivered INTEGER DEFAULT 0
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS codes (
          id TEXT PRIMARY KEY,
          code TEXT UNIQUE,
          reward_points INTEGER DEFAULT 0,
          mission_type TEXT,
          max_uses INTEGER DEFAULT 1,
          uses INTEGER DEFAULT 0,
          expires_at REAL,
          created_at REAL,
          game_code TEXT
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS events (
          id TEXT PRIMARY KEY,
          game_code TEXT,
          event_type TEXT,
          event_data TEXT,
          created_at REAL
        );
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
          id TEXT PRIMARY KEY,
          player_id TEXT,
          game_code TEXT,
          action TEXT,
          details TEXT,
          is_suspicious INTEGER DEFAULT 0,
          created_at REAL
        );
        ''')
        # ── Auto-migración idempotente ──────────────────────────────────
        # Para bases de datos creadas con versiones anteriores del esquema:
        # añade columnas que falten sin borrar datos. Si ya existen, se ignora.
        migrations = [
            ("players",        "finished_at",       "REAL"),
            ("player_missions","status",             "TEXT DEFAULT 'available'"),
            ("player_missions","started_at",         "REAL"),
            ("rewards",        "disabled",           "INTEGER DEFAULT 0"),
            ("rewards",        "description",        "TEXT DEFAULT ''"),
            # Kahoot sync columns
            ("games",          "mission_duration_sec","INTEGER DEFAULT 60"),
            ("games",          "missions_order",     "TEXT DEFAULT '[]'"),
        ]
        for table, col, coltype in migrations:
            try:
                await db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")
            except Exception:
                pass  # La columna ya existe

        # Tabla para resultados por ronda (Kahoot tracking)
        await db.execute('''
        CREATE TABLE IF NOT EXISTS mission_round_results (
          id TEXT PRIMARY KEY,
          game_code TEXT NOT NULL,
          mission_index INTEGER NOT NULL,
          mission_id TEXT,
          player_id TEXT NOT NULL,
          answered INTEGER DEFAULT 0,
          correct INTEGER DEFAULT 0,
          points_earned INTEGER DEFAULT 0,
          time_taken_ms INTEGER,
          created_at REAL
        );
        ''')

        await db.commit()

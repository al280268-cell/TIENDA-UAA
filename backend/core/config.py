from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ABLY_API_KEY: str = ""
    ABLY_CLIENT_KEY: str = ""
    ADMIN_PASSWORD: str = "uaa2026admin"
    DATABASE_URL: str = "sqlite+aiosqlite:///./game.db"
    JWT_SECRET: str = "uaa-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    MAX_PLAYERS_DEFAULT: int = 20
    GAME_DURATION_DEFAULT: int = 180
    REALTIME_PROVIDER: str = "ably"
    # Se guarda como texto plano ("*" o "https://a.com,https://b.com").
    # Pydantic-settings v2 intentaría interpretar una lista como JSON y
    # reventaría con un valor tipo "*", por eso lo parseamos nosotros.
    CORS_ORIGINS: str = "*"

    # Ignora variables extra del .env (p. ej. MAX_PLAYERS_DEFAULT) sin fallar.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "*").strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

settings = Settings()

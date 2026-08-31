from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.config import settings

security = HTTPBearer()

def create_player_token(player_id: str, game_code: str) -> str:
    expires_delta = timedelta(hours=12)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": player_id, "game_code": game_code, "role": "player"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_admin_token() -> str:
    expires_delta = timedelta(hours=4)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "role": "admin"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_player_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("role") != "player":
            raise HTTPException(status_code=401, detail="Invalid role")
        return {"player_id": payload.get("sub"), "game_code": payload.get("game_code")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_admin_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=401, detail="Invalid role")
        return {"role": "admin"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_player(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    return verify_player_token(credentials.credentials)

def get_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    return verify_admin_token(credentials.credentials)

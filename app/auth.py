"""
Simple file-backed user store with bcrypt passwords and JWT tokens.
An admin user is created automatically on first startup.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.schemas import TokenData

_raw_secret = os.getenv("SECRET_KEY", "")
if not _raw_secret:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Set it to a long random string before starting the server."
    )
SECRET_KEY = _raw_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8   # 8 hours

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Where users are persisted between restarts
_USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"


def _load_users() -> dict:
    if _USERS_FILE.exists():
        with open(_USERS_FILE) as f:
            return json.load(f)
    return {}


def _save_users(users: dict) -> None:
    _USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _ensure_admin() -> None:
    """Create a default admin account if no users exist yet."""
    users = _load_users()
    if not users:
        users["admin"] = {
            "username": "admin",
            "hashed_password": _pwd_ctx.hash("admin"),
            "role": "admin",
        }
        _save_users(users)


_ensure_admin()


# ── Public helpers ────────────────────────────────────────────────────────────

def get_user(username: str) -> Optional[dict]:
    return _load_users().get(username)


def create_user(username: str, password: str, role: str = "user") -> dict:
    users = _load_users()
    if username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    users[username] = {
        "username": username,
        "hashed_password": _pwd_ctx.hash(password),
        "role": role,
    }
    _save_users(users)
    return {"username": username, "role": role}


def delete_user(username: str) -> None:
    users = _load_users()
    if username not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[username]
    _save_users(users)


def list_users() -> list:
    return [
        {"username": u["username"], "role": u["role"]}
        for u in _load_users().values()
    ]


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user(username)
    if not user:
        return None
    if not _pwd_ctx.verify(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(_oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

"""Authentication router — login, register."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import auth
from app.models.schemas import Token, UserCreate, UserOut
from app.auth import require_admin, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def read_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}


# ── User management (admin only) ──────────────────────────────────────────────

@router.get("/users", response_model=list)
async def list_users(_: dict = Depends(require_admin)):
    return auth.list_users()


@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, _: dict = Depends(require_admin)):
    return auth.create_user(payload.username, payload.password, payload.role)


@router.delete("/users/{username}", status_code=204)
async def delete_user(username: str, current_user: dict = Depends(require_admin)):
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    auth.delete_user(username)

from fastapi import APIRouter, HTTPException
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth_schema import AuthRegister, AuthLogin, AuthResponse, TokenResponse
from app.models.serializers import auth_serializer
from app.core.security import hash_password, verify_password, create_access_token
from datetime import datetime, timezone


router = APIRouter(prefix="/auth", tags=["auth"])
repo = AuthRepository()


@router.post("/register", response_model=AuthResponse)
def register(payload: AuthRegister):
    existing_user = repo.get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email già registrata")

    # 🔥 CORREZIONE: genera l'hash della password
    hashed_password = hash_password(payload.password)

    user_data = {
    "first_name": payload.first_name,
    "last_name": payload.last_name,
    "email": payload.email,
    "password": hashed_password,
    "agreement_id": payload.agreement_id,
    "accepted_at": datetime.now(timezone.utc)
}


    user_id = repo.create_user(user_data)
    user = repo.get_user_by_id(user_id)
    return auth_serializer(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: AuthLogin):
    user = repo.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="Email o password non validi")

    stored_hash = user.get("password") or ""
    if not verify_password(payload.password, stored_hash):
        raise HTTPException(status_code=401, detail="Email o password non validi")

    token = create_access_token({"user_id": str(user["_id"]), "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

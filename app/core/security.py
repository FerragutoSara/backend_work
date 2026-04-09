import bcrypt
import jwt
from datetime import datetime, timedelta

from app.core.config import JWT_SECRET_KEY

TOKEN_EXPIRATION_SECONDS = 3600


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    except ValueError:
        return False


def create_access_token(payload: dict, expires_in: int = TOKEN_EXPIRATION_SECONDS) -> str:
    payload_data = payload.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_in)
    payload_data["exp"] = expire
    return jwt.encode(payload_data, JWT_SECRET_KEY, algorithm="HS256")

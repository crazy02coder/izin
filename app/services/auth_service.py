from datetime import datetime, timedelta, timezone
from jose import jwt
from pwdlib import PasswordHash
from app.config import settings

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(p):
    return password_hash.hash(p)


def verify_password(p, h):
    return password_hash.verify(p, h)


def create_token(user_id):
    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
        },
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )


def decode_token(token):
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])

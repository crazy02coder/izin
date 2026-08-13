from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.services.auth_service import decode_token


def current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token") or request.headers.get(
        "Authorization", ""
    ).removeprefix("Bearer ")
    if not token:
        raise HTTPException(401, "Oturum gerekli")
    try:
        uid = int(decode_token(token)["sub"])
    except Exception:
        raise HTTPException(401, "Geçersiz oturum")
    user = db.get(User, uid)
    if not user or not user.is_active:
        raise HTTPException(401, "Kullanıcı bulunamadı")
    return user

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import User, AuditLog
from app.schemas import LoginIn, UserOut
from app.services.auth_service import verify_password, create_token
from app.dependencies import current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "E-posta veya şifre hatalı")
    response.set_cookie(
        "access_token",
        create_token(user.id),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 8,
    )
    db.add(AuditLog(actor_user_id=user.id, action="LOGIN", entity_type="USER", entity_id=user.id))
    db.commit()
    return {"user": UserOut.model_validate(user)}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user

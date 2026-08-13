from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import current_user
from app.models import User
from app.schemas import UserOut
from app.services.hierarchy_service import HierarchyService

router = APIRouter(prefix="/api/users", tags=["users"])
hs = HierarchyService()


@router.get("/me", response_model=UserOut)
def my_profile(user=Depends(current_user)):
    return user


@router.get("", response_model=list[UserOut])
def users(db: Session = Depends(get_db), user=Depends(current_user)):
    return hs.visible_users(db, user)


@router.get("/{user_id}", response_model=UserOut)
def user_detail(user_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    target = db.get(User, user_id)
    if not target or not hs.can_view_user(db, user, target):
        raise HTTPException(404, "Kullanıcı bulunamadı")
    return target

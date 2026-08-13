from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import current_user
from app.models import Faculty, Department

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/faculties")
def faculties(db: Session = Depends(get_db), user=Depends(current_user)):
    q = (
        select(Faculty).order_by(Faculty.name)
        if user.system_role in ("RECTOR", "VICE_RECTOR", "ADMIN")
        else select(Faculty).where(Faculty.id == user.faculty_id)
    )
    return [{"id": x.id, "name": x.name} for x in db.scalars(q)]


@router.get("/departments")
def departments(db: Session = Depends(get_db), user=Depends(current_user)):
    fids = [x["id"] for x in faculties(db, user)]
    return [
        {"id": x.id, "name": x.name, "faculty_id": x.faculty_id}
        for x in db.scalars(
            select(Department).where(Department.faculty_id.in_(fids)).order_by(Department.name)
        )
    ]

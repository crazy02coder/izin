from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import current_user
from app.models import Faculty, Department
from app.services.hierarchy_service import HierarchyService

router = APIRouter(prefix="/api", tags=["catalog"])
hierarchy = HierarchyService()


@router.get("/faculties")
def faculties(db: Session = Depends(get_db), user=Depends(current_user)):
    role = hierarchy.get_highest_priority_role(user)
    q = (
        select(Faculty).order_by(Faculty.name)
        if role and role.value in ("RECTOR", "VICE_RECTOR", "ADMIN")
        else select(Faculty).where(Faculty.id == hierarchy.faculty_id_for(db, user))
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

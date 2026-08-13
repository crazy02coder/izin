from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import current_user
from app.models import LeaveRequest, LeaveBalance
from app.services.hierarchy_service import HierarchyService

router = APIRouter(prefix="/api", tags=["dashboard"])
hs = HierarchyService()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(current_user)):
    visible = hs.visible_users(db, user)
    ids = [u.id for u in visible]
    year = date.today().year
    b = db.scalar(
        select(LeaveBalance).where(LeaveBalance.user_id == user.id, LeaveBalance.year == year)
    )
    leaves = (
        list(db.scalars(select(LeaveRequest).where(LeaveRequest.user_id.in_(ids)))) if ids else []
    )
    pending = [x for x in leaves if x.status == "PENDING"]
    today = date.today()
    month_start = today.replace(day=1)
    next_month = (
        date(today.year + 1, 1, 1) if today.month == 12 else date(today.year, today.month + 1, 1)
    )
    active = sum(
        x.start_date <= today <= x.end_date and x.status in ("APPROVED", "AUTO_APPROVED")
        for x in leaves
    )
    planned_month = sum(
        x.status in ("APPROVED", "AUTO_APPROVED", "PENDING")
        and x.start_date < next_month
        and x.end_date >= month_start
        for x in leaves
    )
    recent = [
        {
            "id": x.id,
            "start_date": x.start_date,
            "end_date": x.end_date,
            "working_days": x.working_days,
            "status": x.status,
        }
        for x in leaves[-8:]
    ]
    return {
        "user": user.full_name,
        "role": user.system_role,
        "visible_user_count": len(visible),
        "balance": {
            "total": b.total_days if b else 0,
            "used": b.used_days if b else 0,
            "reserved": b.reserved_days if b else 0,
            "remaining": b.remaining_days if b else 0,
        },
        "stats": {
            "active_leave": active,
            "pending": len(pending),
            "planned_month": planned_month,
            "total_people": len(visible),
        },
        "recent_leaves": recent,
    }


@router.get("/calendar")
def calendar(db: Session = Depends(get_db), user=Depends(current_user)):
    ids = [u.id for u in hs.visible_users(db, user)]
    rows = (
        db.scalars(
            select(LeaveRequest).where(
                LeaveRequest.user_id.in_(ids),
                LeaveRequest.status.in_(["APPROVED", "AUTO_APPROVED", "PENDING"]),
            )
        )
        if ids
        else []
    )
    return [
        {
            "id": x.id,
            "user_id": x.user_id,
            "start_date": x.start_date,
            "end_date": x.end_date,
            "working_days": x.working_days,
            "status": x.status,
        }
        for x in rows
    ]

from datetime import date, timedelta
from sqlalchemy import select
from fastapi import HTTPException
from app.models import Holiday, LeaveRequest, LeaveStatus


def working_days(db, start: date, end: date) -> int:
    if start > end:
        raise HTTPException(400, "Başlangıç tarihi bitiş tarihinden büyük olamaz.")
    holidays = {
        x.date
        for x in db.scalars(select(Holiday).where(Holiday.date >= start, Holiday.date <= end))
    }
    n = 0
    d = start
    while d <= end:
        if d.weekday() < 5 and d not in holidays:
            n += 1
        d += timedelta(days=1)
    return n


def has_overlap(db, user_id, start, end, exclude_id=None):
    q = select(LeaveRequest).where(
        LeaveRequest.user_id == user_id,
        LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
        LeaveRequest.start_date <= end,
        LeaveRequest.end_date >= start,
    )
    if exclude_id:
        q = q.where(LeaveRequest.id != exclude_id)
    return db.scalar(q) is not None

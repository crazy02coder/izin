from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import current_user
from app.models import LeaveRequest, LeaveStatus, LeaveBalance, AuditLog, User
from app.schemas import LeaveCreate, LeaveOut, RejectIn
from app.services.leave_service import working_days, has_overlap
from app.services.leave_workflow_service import LeaveWorkflowService

router = APIRouter(prefix="/api/leaves", tags=["leaves"])
workflow = LeaveWorkflowService()


def balance(db, user, year):
    b = db.scalar(
        select(LeaveBalance).where(LeaveBalance.user_id == user.id, LeaveBalance.year == year)
    )
    if not b:
        raise HTTPException(400, "Bu yıl için izin bakiyesi tanımlanmamış")
    return b


@router.get("/my", response_model=list[LeaveOut])
def mine(db: Session = Depends(get_db), user=Depends(current_user)):
    return list(
        db.scalars(
            select(LeaveRequest)
            .where(LeaveRequest.user_id == user.id)
            .order_by(LeaveRequest.created_at.desc())
        )
    )


@router.post("", response_model=LeaveOut)
def create(data: LeaveCreate, db: Session = Depends(get_db), user=Depends(current_user)):
    days = working_days(db, data.start_date, data.end_date)
    if days < 1:
        raise HTTPException(400, "En az bir iş günü seçilmelidir")
    if has_overlap(db, user.id, data.start_date, data.end_date):
        raise HTTPException(400, "Tarih aralığında mevcut izin başvurusu var")
    b = balance(db, user, data.start_date.year)
    if b.remaining_days < days:
        raise HTTPException(400, "Kalan izin bakiyesi yetersiz")
    status = LeaveStatus.PENDING
    leave = LeaveRequest(
        user_id=user.id,
        leave_type=data.leave_type.value,
        start_date=data.start_date,
        end_date=data.end_date,
        working_days=days,
        reason=data.reason,
        status=status,
    )
    db.add(leave)
    db.flush()
    leave.approval_steps = workflow.build_workflow(db, user, data.leave_type)
    b.reserved_days += days
    db.add(
        AuditLog(
            actor_user_id=user.id, action="LEAVE_CREATED", entity_type="LEAVE", entity_id=leave.id
        )
    )
    db.commit()
    db.refresh(leave)
    return leave


@router.get("/pending-approvals", response_model=list[LeaveOut])
def pending(db: Session = Depends(get_db), user=Depends(current_user)):
    return workflow.pending_for_user(db, user)


@router.post("/{leave_id}/approve", response_model=LeaveOut)
def approve(leave_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(404, "İzin talebi bulunamadı")
    was_final = leave.status == LeaveStatus.APPROVED
    workflow.approve_step(db, leave, user)
    if not was_final and leave.status == LeaveStatus.APPROVED:
        b = balance(db, db.get(User, leave.user_id), leave.start_date.year)
        b.reserved_days = max(0, b.reserved_days - leave.working_days)
        b.used_days += leave.working_days
    db.add(
        AuditLog(
            actor_user_id=user.id, action="LEAVE_APPROVED", entity_type="LEAVE", entity_id=leave.id
        )
    )
    db.commit()
    return leave


@router.post("/{leave_id}/reject", response_model=LeaveOut)
def reject(
    leave_id: int, data: RejectIn, db: Session = Depends(get_db), user=Depends(current_user)
):
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(404, "İzin talebi bulunamadı")
    b = balance(db, db.get(User, leave.user_id), leave.start_date.year)
    b.reserved_days = max(0, b.reserved_days - leave.working_days)
    workflow.reject_step(leave, user, data.rejection_reason)
    db.add(
        AuditLog(
            actor_user_id=user.id, action="LEAVE_REJECTED", entity_type="LEAVE", entity_id=leave.id
        )
    )
    db.commit()
    return leave


@router.post("/{leave_id}/cancel", response_model=LeaveOut)
def cancel(leave_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    leave = db.get(LeaveRequest, leave_id)
    if not leave or leave.user_id != user.id or leave.status not in ("PENDING", "APPROVED"):
        raise HTTPException(403, "İzin iptal edilemez")
    b = balance(db, user, leave.start_date.year)
    b.reserved_days = max(0, b.reserved_days - leave.working_days)
    b.used_days = max(0, b.used_days - (leave.working_days if leave.status == "APPROVED" else 0))
    leave.status = "CANCELLED"
    for step in leave.approval_steps:
        if step.status in ("PENDING", "WAITING"):
            step.status = "SKIPPED"
    db.add(
        AuditLog(
            actor_user_id=user.id, action="LEAVE_CANCELLED", entity_type="LEAVE", entity_id=leave.id
        )
    )
    db.commit()
    return leave

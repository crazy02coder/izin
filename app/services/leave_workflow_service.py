from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select

from app.models import (
    AdministrativeRoleType,
    ApprovalStepStatus,
    ApprovalStepType,
    LeaveApprovalStep,
    LeaveRequest,
    LeaveStatus,
    LeaveType,
    User,
)
from app.services.hierarchy_service import HierarchyService


class LeaveWorkflowService:
    def __init__(self):
        self.hierarchy = HierarchyService()

    def build_workflow(self, db, user, leave_type):
        highest = self.hierarchy.get_highest_priority_role(user)
        faculty_id = self.hierarchy.faculty_id_for(db, user)
        department_id = self.hierarchy.department_id_for(db, user)

        if highest == AdministrativeRoleType.RECTOR:
            definitions = [(AdministrativeRoleType.BOARD_CHAIRMAN, ApprovalStepType.BOARD_DECISION)]
        elif highest in (AdministrativeRoleType.VICE_RECTOR, AdministrativeRoleType.DEAN):
            definitions = [(AdministrativeRoleType.RECTOR, ApprovalStepType.FINAL_APPROVAL)]
        elif leave_type == LeaveType.ANNUAL:
            definitions = [
                (AdministrativeRoleType.DEPARTMENT_HEAD, ApprovalStepType.REVIEW),
                (AdministrativeRoleType.HR_DIRECTOR, ApprovalStepType.HR_CONTROL),
                (AdministrativeRoleType.DEAN, ApprovalStepType.FINAL_APPROVAL),
            ]
        else:
            definitions = [
                (AdministrativeRoleType.DEPARTMENT_HEAD, ApprovalStepType.REVIEW),
                (AdministrativeRoleType.DEAN, ApprovalStepType.FINAL_APPROVAL),
            ]

        steps = []
        for index, (required_role, step_type) in enumerate(definitions, start=1):
            assigned = self._assigned_user(
                db,
                required_role,
                faculty_id=faculty_id,
                department_id=department_id,
            )
            if assigned and assigned.id == user.id:
                raise HTTPException(400, "Kullanıcı kendi izin adımını onaylayamaz")
            steps.append(
                LeaveApprovalStep(
                    step_order=index,
                    step_type=step_type,
                    required_role=required_role,
                    assigned_user_id=assigned.id if assigned else None,
                    status=ApprovalStepStatus.PENDING if index == 1 else ApprovalStepStatus.WAITING,
                )
            )
        if not steps or steps[0].assigned_user_id is None:
            raise HTTPException(400, "İzin onay zinciri için yetkili kullanıcı bulunamadı")
        return steps

    def _assigned_user(self, db, required_role, faculty_id=None, department_id=None):
        if required_role == AdministrativeRoleType.DEPARTMENT_HEAD:
            return self.hierarchy.find_assigned_user(db, required_role, department_id=department_id)
        if required_role == AdministrativeRoleType.DEAN:
            return self.hierarchy.find_assigned_user(db, required_role, faculty_id=faculty_id)
        return self.hierarchy.find_assigned_user(db, required_role)

    def get_current_step(self, leave_request):
        return next(
            (
                step
                for step in leave_request.approval_steps
                if step.status == ApprovalStepStatus.PENDING
            ),
            None,
        )

    def approve_step(self, db, leave_request, actor, comment=None):
        step = self._authorized_current_step(leave_request, actor)
        step.status = ApprovalStepStatus.APPROVED
        step.comment = comment
        step.acted_at = datetime.utcnow()
        next_step = next(
            (
                item
                for item in leave_request.approval_steps
                if item.step_order > step.step_order and item.status == ApprovalStepStatus.WAITING
            ),
            None,
        )
        if next_step:
            next_step.status = ApprovalStepStatus.PENDING
        else:
            leave_request.status = LeaveStatus.APPROVED
            leave_request.approved_at = datetime.utcnow()
        return step

    def reject_step(self, leave_request, actor, reason):
        step = self._authorized_current_step(leave_request, actor)
        step.status = ApprovalStepStatus.REJECTED
        step.comment = reason
        step.acted_at = datetime.utcnow()
        leave_request.status = LeaveStatus.REJECTED
        leave_request.rejected_at = datetime.utcnow()
        leave_request.rejection_reason = reason
        return step

    def _authorized_current_step(self, leave_request, actor):
        step = self.get_current_step(leave_request)
        if not step or step.assigned_user_id != actor.id or leave_request.user_id == actor.id:
            raise HTTPException(403, "Bu izin adımında işlem yapma yetkiniz yok")
        return step

    def pending_for_user(self, db, user):
        return list(
            db.scalars(
                select(LeaveRequest)
                .join(LeaveApprovalStep)
                .where(
                    LeaveApprovalStep.assigned_user_id == user.id,
                    LeaveApprovalStep.status == ApprovalStepStatus.PENDING,
                )
                .order_by(LeaveRequest.start_date)
            ).unique()
        )

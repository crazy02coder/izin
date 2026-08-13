from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import (
    AcademicTitle,
    AdministrativeRoleType,
    Department,
    Faculty,
    LeaveApprovalStep,
    LeaveRequest,
    LeaveType,
    User,
    UserAdministrativeRole,
)
from app.services.leave_workflow_service import LeaveWorkflowService
from app.services.hierarchy_service import HierarchyService


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def make_people(db):
    faculty = Faculty(name="Mühendislik")
    db.add(faculty)
    db.flush()
    department = Department(name="Yazılım Mühendisliği", faculty_id=faculty.id)
    db.add(department)
    db.flush()

    people = {
        "academic": User(
            first_name="Hasan",
            last_name="Erbay",
            email="hasan@example.test",
            password_hash="x",
            academic_title=AcademicTitle.PROFESSOR,
            system_role="ACADEMIC",
            faculty_id=faculty.id,
            department_id=department.id,
        ),
        "head": User(
            first_name="Meltem",
            last_name="Eryılmaz",
            email="meltem@example.test",
            password_hash="x",
            academic_title=AcademicTitle.PROFESSOR,
            system_role="ACADEMIC",
            faculty_id=faculty.id,
            department_id=department.id,
        ),
        "dean": User(
            first_name="Serdar",
            last_name="Müldür",
            email="serdar@example.test",
            password_hash="x",
            academic_title=AcademicTitle.PROFESSOR,
            system_role="ACADEMIC",
            faculty_id=faculty.id,
        ),
        "hr": User(
            first_name="Esra",
            last_name="Demirci",
            email="esra@example.test",
            password_hash="x",
            academic_title=AcademicTitle.OTHER,
            system_role="ADMIN",
        ),
    }
    db.add_all(people.values())
    db.flush()
    db.add_all(
        [
            UserAdministrativeRole(
                user_id=people["head"].id,
                role_type=AdministrativeRoleType.DEPARTMENT_HEAD,
                faculty_id=faculty.id,
                department_id=department.id,
            ),
            UserAdministrativeRole(
                user_id=people["dean"].id,
                role_type=AdministrativeRoleType.DEAN,
                faculty_id=faculty.id,
            ),
            UserAdministrativeRole(
                user_id=people["hr"].id,
                role_type=AdministrativeRoleType.HR_DIRECTOR,
            ),
        ]
    )
    db.commit()
    return people


def make_leave(db, academic):
    leave = LeaveRequest(
        user_id=academic.id,
        leave_type=LeaveType.ANNUAL,
        start_date=date(2026, 9, 7),
        end_date=date(2026, 9, 11),
        working_days=5,
        status="PENDING",
    )
    db.add(leave)
    db.flush()
    leave.approval_steps = LeaveWorkflowService().build_workflow(db, academic, LeaveType.ANNUAL)
    db.commit()
    return leave


def test_three_step_workflow_reaches_approved(db):
    people = make_people(db)
    leave = make_leave(db, people["academic"])
    service = LeaveWorkflowService()

    assert [(step.required_role, step.status) for step in leave.approval_steps] == [
        ("DEPARTMENT_HEAD", "PENDING"),
        ("HR_DIRECTOR", "WAITING"),
        ("DEAN", "WAITING"),
    ]
    service.approve_step(db, leave, people["head"])
    db.commit()
    assert leave.approval_steps[1].status == "PENDING"
    service.approve_step(db, leave, people["hr"])
    db.commit()
    assert leave.approval_steps[2].status == "PENDING"
    service.approve_step(db, leave, people["dean"])
    db.commit()
    assert leave.status == "APPROVED"


def test_unauthorized_user_cannot_approve_current_step(db):
    people = make_people(db)
    leave = make_leave(db, people["academic"])

    with pytest.raises(HTTPException) as error:
        LeaveWorkflowService().approve_step(db, leave, people["dean"])
    assert error.value.status_code == 403


def test_rejecting_current_step_rejects_request(db):
    people = make_people(db)
    leave = make_leave(db, people["academic"])

    LeaveWorkflowService().reject_step(leave, people["head"], "Uygun değil")
    assert leave.status == "REJECTED"
    assert leave.approval_steps[0].status == "REJECTED"
    assert all(step.status == "WAITING" for step in leave.approval_steps[1:])


def test_highest_active_role_is_used_for_a_multi_role_user(db):
    people = make_people(db)
    people["academic"].administrative_roles.append(
        UserAdministrativeRole(
            user_id=people["academic"].id, role_type=AdministrativeRoleType.VICE_RECTOR
        )
    )
    db.commit()
    assert (
        HierarchyService().get_highest_priority_role(people["academic"])
        == AdministrativeRoleType.VICE_RECTOR
    )

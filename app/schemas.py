from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models import LeaveStatus, LeaveType


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    email: str
    academic_title: str
    system_role: str
    faculty_id: int | None = None
    department_id: int | None = None
    profile_photo_url: str | None = None
    is_active: bool
    must_change_password: bool


class LeaveCreate(BaseModel):
    leave_type: LeaveType = LeaveType.ANNUAL
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    leave_type: str
    start_date: date
    end_date: date
    working_days: int
    reason: str | None = None
    status: str
    approver_id: int | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None
    rejection_reason: str | None = None


class RejectIn(BaseModel):
    rejection_reason: str = Field(min_length=3, max_length=1000)

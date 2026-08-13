from datetime import date as dt_date, datetime
from enum import Enum
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AcademicTitle(str, Enum):
    PROFESSOR = "PROFESSOR"
    ASSOCIATE_PROFESSOR = "ASSOCIATE_PROFESSOR"
    ASSISTANT_PROFESSOR = "ASSISTANT_PROFESSOR"
    LECTURER = "LECTURER"
    RESEARCH_ASSISTANT = "RESEARCH_ASSISTANT"
    OTHER = "OTHER"


class SystemRole(str, Enum):
    RECTOR = "RECTOR"
    VICE_RECTOR = "VICE_RECTOR"
    DEAN = "DEAN"
    VICE_DEAN = "VICE_DEAN"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    ACADEMIC = "ACADEMIC"
    ADMIN = "ADMIN"


class LeaveType(str, Enum):
    ANNUAL = "ANNUAL"
    EXCUSE = "EXCUSE"
    SICK = "SICK"
    OTHER = "OTHER"


class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    AUTO_APPROVED = "AUTO_APPROVED"
    RECORD_ONLY = "RECORD_ONLY"


class University(Base):
    __tablename__ = "universities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)


class Faculty(Base):
    __tablename__ = "faculties"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    dean_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"))
    department_head_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    __table_args__ = (UniqueConstraint("name", "faculty_id"),)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(500))
    academic_title: Mapped[AcademicTitle] = mapped_column(String(40), default=AcademicTitle.OTHER)
    system_role: Mapped[SystemRole] = mapped_column(String(40), default=SystemRole.ACADEMIC)
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculties.id"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))
    profile_photo_url: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class LeavePolicy(Base):
    __tablename__ = "leave_policies"
    id: Mapped[int] = mapped_column(primary_key=True)
    academic_title: Mapped[str] = mapped_column(String(40), unique=True)
    annual_days: Mapped[int] = mapped_column(Integer)


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    year: Mapped[int] = mapped_column(Integer)
    total_days: Mapped[int] = mapped_column(Integer)
    used_days: Mapped[int] = mapped_column(Integer, default=0)
    reserved_days: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("user_id", "year"),)

    @property
    def remaining_days(self):
        return self.total_days - self.used_days - self.reserved_days


class Holiday(Base):
    __tablename__ = "holidays"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt_date] = mapped_column(Date, unique=True)
    name: Mapped[str] = mapped_column(String(200))


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    leave_type: Mapped[LeaveType] = mapped_column(String(30))
    start_date: Mapped[dt_date] = mapped_column(Date)
    end_date: Mapped[dt_date] = mapped_column(Date)
    working_days: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[LeaveStatus] = mapped_column(String(30), default=LeaveStatus.PENDING)
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

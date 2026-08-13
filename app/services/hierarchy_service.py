from sqlalchemy import select

from app.models import (
    AdministrativeRoleType,
    Department,
    Faculty,
    SystemRole,
    User,
    UserAdministrativeRole,
)

ROLE_PRIORITY = {
    AdministrativeRoleType.RECTOR: 100,
    AdministrativeRoleType.VICE_RECTOR: 90,
    AdministrativeRoleType.DEAN: 80,
    AdministrativeRoleType.VICE_DEAN: 70,
    AdministrativeRoleType.DEPARTMENT_HEAD: 60,
    AdministrativeRoleType.HR_DIRECTOR: 50,
    AdministrativeRoleType.BOARD_CHAIRMAN: 40,
    AdministrativeRoleType.ADMIN: 10,
}


class HierarchyService:
    def get_active_roles(self, user):
        roles = []
        for role in user.administrative_roles:
            if role.is_active:
                try:
                    roles.append(AdministrativeRoleType(role.role_type))
                except ValueError:
                    continue
        if roles:
            return roles
        # Compatibility for an existing database before role migration.
        try:
            legacy = AdministrativeRoleType(user.system_role)
        except ValueError:
            return []
        return (
            []
            if legacy == AdministrativeRoleType.ADMIN and user.system_role == "ACADEMIC"
            else [legacy]
        )

    def has_role(self, user, role_type):
        role = (
            role_type
            if isinstance(role_type, AdministrativeRoleType)
            else AdministrativeRoleType(role_type)
        )
        return role in self.get_active_roles(user)

    def get_highest_priority_role(self, user):
        roles = self.get_active_roles(user)
        return max(roles, key=lambda role: ROLE_PRIORITY.get(role, -1), default=None)

    def role_records(self, db, user, role_type):
        return list(
            db.scalars(
                select(UserAdministrativeRole).where(
                    UserAdministrativeRole.user_id == user.id,
                    UserAdministrativeRole.role_type == role_type,
                    UserAdministrativeRole.is_active.is_(True),
                )
            )
        )

    def find_assigned_user(self, db, role_type, faculty_id=None, department_id=None):
        query = select(UserAdministrativeRole).where(
            UserAdministrativeRole.role_type == role_type,
            UserAdministrativeRole.is_active.is_(True),
        )
        if department_id is not None:
            query = query.where(UserAdministrativeRole.department_id == department_id)
        elif faculty_id is not None:
            query = query.where(UserAdministrativeRole.faculty_id == faculty_id)
        # No scope means a university-wide role. Legacy rows may contain
        # copied faculty/department values, so they must still be eligible.
        role = db.scalar(query)
        if role:
            return db.get(User, role.user_id)
        # Backward compatibility for databases seeded before the role table
        # was introduced.
        return db.scalar(
            select(User).where(
                User.system_role == role_type.value,
                User.is_active.is_(True),
            )
        )

    def faculty_id_for(self, db, user):
        role = self.get_highest_priority_role(user)
        records = self.role_records(db, user, role) if role else []
        return records[0].faculty_id if records and records[0].faculty_id else user.faculty_id

    def department_id_for(self, db, user):
        role = self.get_highest_priority_role(user)
        records = self.role_records(db, user, role) if role else []
        return (
            records[0].department_id if records and records[0].department_id else user.department_id
        )

    def visible_users(self, db, actor):
        q = select(User).where(User.is_active.is_(True))
        role = self.get_highest_priority_role(actor)
        if role is None:
            return [actor]
        if role in (
            AdministrativeRoleType.RECTOR,
            AdministrativeRoleType.VICE_RECTOR,
            AdministrativeRoleType.HR_DIRECTOR,
            AdministrativeRoleType.BOARD_CHAIRMAN,
            AdministrativeRoleType.ADMIN,
        ):
            return list(db.scalars(q.order_by(User.last_name, User.first_name)))
        if role == AdministrativeRoleType.DEPARTMENT_HEAD:
            q = q.where(User.department_id == self.department_id_for(db, actor))
        elif role in (AdministrativeRoleType.DEAN, AdministrativeRoleType.VICE_DEAN):
            q = q.where(User.faculty_id == self.faculty_id_for(db, actor))
        else:
            return [actor]
        return list(db.scalars(q.order_by(User.last_name, User.first_name)))

    def can_view_user(self, db, actor, target):
        return target.id in {user.id for user in self.visible_users(db, actor)}

    def legacy_approver(self, db, user):
        if self.has_role(user, AdministrativeRoleType.RECTOR):
            return None
        if self.has_role(user, AdministrativeRoleType.VICE_RECTOR) or self.has_role(
            user, AdministrativeRoleType.DEAN
        ):
            return self.find_assigned_user(db, AdministrativeRoleType.RECTOR)
        if self.has_role(user, AdministrativeRoleType.DEPARTMENT_HEAD):
            department = db.get(Department, user.department_id)
            return db.get(
                User, department.faculty_id and db.get(Faculty, department.faculty_id).dean_user_id
            )
        if user.department_id:
            department = db.get(Department, user.department_id)
            return db.get(User, department.department_head_user_id) if department else None
        return self.find_assigned_user(db, AdministrativeRoleType.RECTOR)

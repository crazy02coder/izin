from sqlalchemy import select, or_
from app.models import User, Faculty, Department, SystemRole


class HierarchyService:
    def approver(self, db, user):
        if user.system_role == SystemRole.RECTOR:
            return None
        if user.system_role in (SystemRole.VICE_RECTOR, SystemRole.DEAN):
            return self._rector(db)
        if user.system_role == SystemRole.DEPARTMENT_HEAD:
            d = db.get(Department, user.department_id)
            return (
                db.get(User, d.faculty_id and db.get(Faculty, d.faculty_id).dean_user_id)
                if d
                else None
            )
        if user.system_role == SystemRole.VICE_DEAN:
            f = db.get(Faculty, user.faculty_id)
            return db.get(User, f.dean_user_id) if f else self._rector(db)
        if user.department_id:
            d = db.get(Department, user.department_id)
            return db.get(User, d.department_head_user_id) if d else self._rector(db)
        return self._rector(db)

    def _rector(self, db):
        return db.scalar(
            select(User).where(User.system_role == SystemRole.RECTOR, User.is_active.is_(True))
        )

    def visible_users(self, db, actor):
        q = select(User).where(User.is_active.is_(True))
        role = actor.system_role
        if role == SystemRole.ACADEMIC:
            return [actor]
        if role == SystemRole.DEPARTMENT_HEAD:
            q = q.where(User.department_id == actor.department_id)
        elif role in (SystemRole.DEAN, SystemRole.VICE_DEAN):
            q = q.where(User.faculty_id == actor.faculty_id)
        elif role not in (SystemRole.RECTOR, SystemRole.VICE_RECTOR, SystemRole.ADMIN):
            return [actor]
        return list(db.scalars(q.order_by(User.last_name, User.first_name)))

    def can_view_user(self, db, actor, target):
        return target.id in {u.id for u in self.visible_users(db, actor)}

    def can_act_on_leave(self, db, actor, leave):
        return (
            leave.approver_id == actor.id
            and leave.user_id != actor.id
            and leave.status == "PENDING"
        )

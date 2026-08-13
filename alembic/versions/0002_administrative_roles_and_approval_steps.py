from alembic import op
from sqlalchemy import text

from app.database import Base
from app import models

revision = "0002_roles_and_approval_steps"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    # create_all is intentional here: it adds only the two new tables while
    # preserving every existing SQLite table and row.
    Base.metadata.create_all(bind)
    bind.execute(text("""
            INSERT INTO user_administrative_roles
                (user_id, role_type, faculty_id, department_id, is_active, created_at, updated_at)
            SELECT id, system_role, faculty_id, department_id, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            FROM users
            WHERE system_role IN
                ('RECTOR', 'VICE_RECTOR', 'DEAN', 'VICE_DEAN', 'DEPARTMENT_HEAD', 'ADMIN')
              AND NOT EXISTS (
                SELECT 1 FROM user_administrative_roles r
                WHERE r.user_id = users.id AND r.role_type = users.system_role
              )
            """))


def downgrade():
    bind = op.get_bind()
    bind.execute(text("DROP TABLE IF EXISTS leave_approval_steps"))
    bind.execute(text("DROP TABLE IF EXISTS user_administrative_roles"))

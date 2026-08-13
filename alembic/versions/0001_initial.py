from app.database import Base
from app import models


def upgrade():
    # Initial schema is declared by the SQLAlchemy models and is suitable for
    # a clean SQLite installation.
    bind = __import__("alembic").op.get_bind()
    Base.metadata.create_all(bind)


def downgrade():
    bind = __import__("alembic").op.get_bind()
    Base.metadata.drop_all(bind)

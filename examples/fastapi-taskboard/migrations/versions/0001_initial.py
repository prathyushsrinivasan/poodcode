"""Create users and tasks; ownership is a database constraint."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("username", sa.String(50), nullable=False, unique=True),
                    sa.Column("password_hash", sa.String(255), nullable=False),
                    sa.Column("active", sa.Boolean(), nullable=False))
    op.create_table("tasks", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("title", sa.String(120), nullable=False),
                    sa.Column("done", sa.Boolean(), nullable=False),
                    sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False))
    op.create_index("ix_tasks_owner_id_id", "tasks", ["owner_id", "id"])


def downgrade():
    op.drop_index("ix_tasks_owner_id_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("users")

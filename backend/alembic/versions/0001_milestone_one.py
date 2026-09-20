"""Add generation metadata to meal plans.

Revision ID: 0001_milestone_one
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_milestone_one"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "mealplan" not in inspector.get_table_names():
        op.create_table(
            "mealplan",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("plan_json", sa.String(), nullable=False),
            sa.Column("generation_metadata_json", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_mealplan_user_id", "mealplan", ["user_id"], unique=False)
        return

    columns = {column["name"] for column in inspector.get_columns("mealplan")}
    if "generation_metadata_json" not in columns:
        op.add_column("mealplan", sa.Column("generation_metadata_json", sa.String(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "mealplan" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("mealplan")}
    if "generation_metadata_json" in columns:
        with op.batch_alter_table("mealplan") as batch_op:
            batch_op.drop_column("generation_metadata_json")

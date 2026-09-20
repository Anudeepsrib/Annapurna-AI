"""Add meal execution, feedback, and leftovers.

Revision ID: 0003_household_activity
Revises: 0002_pantry_v2
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_household_activity"
down_revision = "0002_pantry_v2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "meal_execution",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.String(), nullable=False),
        sa.Column("meal_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["mealplan.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "plan_id", "day", "meal_type", name="uq_meal_execution_slot"),
    )
    op.create_index("ix_meal_execution_plan_id", "meal_execution", ["plan_id"], unique=False)
    op.create_index("ix_meal_execution_user_id", "meal_execution", ["user_id"], unique=False)

    op.create_table(
        "meal_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.String(), nullable=False),
        sa.Column("meal_type", sa.String(), nullable=False),
        sa.Column("signal", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["mealplan.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "plan_id",
            "day",
            "meal_type",
            "signal",
            name="uq_meal_feedback_signal",
        ),
    )
    op.create_index("ix_meal_feedback_plan_id", "meal_feedback", ["plan_id"], unique=False)
    op.create_index("ix_meal_feedback_user_id", "meal_feedback", ["user_id"], unique=False)

    op.create_table(
        "leftover",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("source_plan_id", sa.Integer(), nullable=False),
        sa.Column("source_day", sa.String(), nullable=False),
        sa.Column("source_meal_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("servings_remaining", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("usable_until", sa.DateTime(), nullable=False),
        sa.Column("consumed", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["source_plan_id"], ["mealplan.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "source_plan_id",
            "source_day",
            "source_meal_type",
            name="uq_leftover_source_meal",
        ),
    )
    op.create_index("ix_leftover_source_plan_id", "leftover", ["source_plan_id"], unique=False)
    op.create_index("ix_leftover_user_id", "leftover", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leftover_user_id", table_name="leftover")
    op.drop_index("ix_leftover_source_plan_id", table_name="leftover")
    op.drop_table("leftover")
    op.drop_index("ix_meal_feedback_user_id", table_name="meal_feedback")
    op.drop_index("ix_meal_feedback_plan_id", table_name="meal_feedback")
    op.drop_table("meal_feedback")
    op.drop_index("ix_meal_execution_user_id", table_name="meal_execution")
    op.drop_index("ix_meal_execution_plan_id", table_name="meal_execution")
    op.drop_table("meal_execution")

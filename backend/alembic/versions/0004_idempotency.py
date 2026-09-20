"""Add idempotent plan-generation requests.

Revision ID: 0004_idempotency
Revises: 0003_household_activity
"""

import sqlalchemy as sa

from alembic import op

revision = "0004_idempotency"
down_revision = "0003_household_activity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "generation_request",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("request_hash", sa.String(), nullable=False),
        sa.Column("response_json", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_generation_request_user_key"),
    )
    op.create_index("ix_generation_request_user_id", "generation_request", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_generation_request_user_id", table_name="generation_request")
    op.drop_table("generation_request")

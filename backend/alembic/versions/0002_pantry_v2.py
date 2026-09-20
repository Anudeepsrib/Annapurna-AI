"""Add structured pantry inventory and transactions.

Revision ID: 0002_pantry_v2
Revises: 0001_milestone_one
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_pantry_v2"
down_revision = "0001_milestone_one"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pantry_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("identity_key", sa.String(), nullable=False),
        sa.Column("ingredient_id", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("quantity_value", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("quantity_text", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("storage_location", sa.String(), nullable=False),
        sa.Column("opened", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("minimum_stock_quantity", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("minimum_stock_unit", sa.String(), nullable=True),
        sa.Column("preferred_brand", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "identity_key", name="uq_pantry_item_user_identity"),
    )
    op.create_index("ix_pantry_item_ingredient_id", "pantry_item", ["ingredient_id"], unique=False)
    op.create_index("ix_pantry_item_user_id", "pantry_item", ["user_id"], unique=False)

    op.create_table(
        "pantry_transaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pantry_item_id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("resulting_quantity", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["pantry_item_id"], ["pantry_item.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pantry_transaction_pantry_item_id",
        "pantry_transaction",
        ["pantry_item_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pantry_transaction_pantry_item_id", table_name="pantry_transaction")
    op.drop_table("pantry_transaction")
    op.drop_index("ix_pantry_item_user_id", table_name="pantry_item")
    op.drop_index("ix_pantry_item_ingredient_id", table_name="pantry_item")
    op.drop_table("pantry_item")

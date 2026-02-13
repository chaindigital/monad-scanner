"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2026-02-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "blocks",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("chain_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("number", sa.BigInteger(), nullable=False, index=True),
        sa.Column("hash", sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column("parent_hash", sa.String(length=128), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tx_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_blocks_chain_number", "blocks", ["chain_id", "number"], unique=True)

    op.create_table(
        "scans",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("chain_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("block_number", sa.BigInteger(), nullable=False, index=True),
        sa.Column("block_hash", sa.String(length=128), nullable=False, index=True),
        sa.Column("status", sa.String(length=32), nullable=False, index=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
    )
    op.create_index("ix_scans_chain_block", "scans", ["chain_id", "block_number"], unique=True)

    op.create_table(
        "signals",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("signal_id", sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column("chain_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("block_number", sa.BigInteger(), nullable=False, index=True),
        sa.Column("category", sa.String(length=48), nullable=False, index=True),
        sa.Column("severity", sa.Integer(), nullable=False, index=True),
        sa.Column("confidence", sa.Float(), nullable=False, index=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=True),
        sa.Column("recommended_actions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_signals_chain_block", "signals", ["chain_id", "block_number"], unique=False)


def downgrade():
    op.drop_index("ix_signals_chain_block", table_name="signals")
    op.drop_table("signals")
    op.drop_index("ix_scans_chain_block", table_name="scans")
    op.drop_table("scans")
    op.drop_index("ix_blocks_chain_number", table_name="blocks")
    op.drop_table("blocks")

"""Initial migration for PTE-QR system

Revision ID: 0001
Revises:
Create Date: 2024-09-16 21:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS pte_qr")

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("external_provider", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
        schema="pte_qr",
    )

    # Create documents table
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doc_uid", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("document_type", sa.String(length=50), nullable=True),
        sa.Column("current_revision", sa.String(length=20), nullable=True),
        sa.Column("current_page", sa.Integer(), nullable=True),
        sa.Column("business_status", sa.String(length=50), nullable=True),
        sa.Column("enovia_state", sa.String(length=50), nullable=True),
        sa.Column("is_actual", sa.Boolean(), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("superseded_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["pte_qr.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["pte_qr.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doc_uid"),
        schema="pte_qr",
    )

    # Create qr_codes table
    op.create_table(
        "qr_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doc_uid", sa.String(length=100), nullable=False),
        sa.Column("revision", sa.String(length=20), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("qr_data", sa.Text(), nullable=False),
        sa.Column("hmac_signature", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["pte_qr.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doc_uid", "revision", "page"),
        schema="pte_qr",
    )

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("table_name", sa.String(length=100), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("old_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["pte_qr.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pte_qr",
    )

    # Create user_sessions table
    op.create_table(
        "user_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_token", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_accessed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pte_qr.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token"),
        schema="pte_qr",
    )

    # Create system_settings table
    op.create_table(
        "system_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_encrypted", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["pte_qr.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
        schema="pte_qr",
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop tables in reverse order
    op.drop_table("system_settings", schema="pte_qr")
    op.drop_table("user_sessions", schema="pte_qr")
    op.drop_table("audit_logs", schema="pte_qr")
    op.drop_table("qr_codes", schema="pte_qr")
    op.drop_table("documents", schema="pte_qr")
    op.drop_table("users", schema="pte_qr")

    # Drop schema
    op.execute("DROP SCHEMA IF EXISTS pte_qr CASCADE")

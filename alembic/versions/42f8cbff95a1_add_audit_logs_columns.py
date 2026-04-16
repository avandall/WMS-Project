"""add_audit_logs_columns

Revision ID: 42f8cbff95a1
Revises: 20260415_164500
Create Date: 2026-04-16 08:08:58.877725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42f8cbff95a1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to audit_logs table
    op.add_column('audit_logs', sa.Column('path', sa.String(length=255), nullable=True))
    op.add_column('audit_logs', sa.Column('method', sa.String(length=10), nullable=True))
    op.add_column('audit_logs', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('audit_logs', sa.Column('client_ip', sa.String(length=45), nullable=True))
    op.add_column('audit_logs', sa.Column('user_agent', sa.String(length=500), nullable=True))
    op.add_column('audit_logs', sa.Column('latency_ms', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove the columns in reverse order
    op.drop_column('audit_logs', 'latency_ms')
    op.drop_column('audit_logs', 'user_agent')
    op.drop_column('audit_logs', 'client_ip')
    op.drop_column('audit_logs', 'status_code')
    op.drop_column('audit_logs', 'method')
    op.drop_column('audit_logs', 'path')

"""add user roles and forced password changes

Revision ID: 0007_user_security
Revises: 0006_media_rating_opinions
"""
from alembic import op
import sqlalchemy as sa

revision='0007_user_security'
down_revision='0006_media_rating_opinions'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE users SET is_admin = TRUE WHERE lower(name) LIKE '%joa%' OR lower(name) LIKE '%joaqu%'")
    op.alter_column('users','is_admin',server_default=None)
    op.alter_column('users','must_change_password',server_default=None)


def downgrade():
    op.drop_column('users','must_change_password')
    op.drop_column('users','is_admin')

"""add optional category to place visits

Revision ID: 0004_place_category
Revises: 0003_nullable_test_results
"""
from alembic import op
import sqlalchemy as sa

revision = '0004_place_category'
down_revision = '0003_nullable_test_results'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('place_visits') as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=6), nullable=True))


def downgrade():
    with op.batch_alter_table('place_visits') as batch_op:
        batch_op.drop_column('category')

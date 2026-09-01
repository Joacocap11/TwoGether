"""add optional opinions to media ratings

Revision ID: 0006_media_rating_opinions
Revises: 0005_media_hotels
"""
from alembic import op
import sqlalchemy as sa

revision='0006_media_rating_opinions'
down_revision='0005_media_hotels'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('media_ratings', sa.Column('opinion', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('media_ratings', 'opinion')

"""add hotel pool and breakfast amenities

Revision ID: 0011_hotel_amenities
Revises: 0010_spots
"""
from alembic import op
import sqlalchemy as sa

revision = '0011_hotel_amenities'
down_revision = '0010_spots'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('hotel_visits', sa.Column('has_pool', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('hotel_visits', sa.Column('pool_heated', sa.Boolean(), nullable=True))
    op.add_column('hotel_visits', sa.Column('pool_rating', sa.Integer(), nullable=True))
    op.add_column('hotel_visits', sa.Column('has_breakfast', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('hotel_visits', sa.Column('breakfast_rating', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('hotel_visits', 'breakfast_rating')
    op.drop_column('hotel_visits', 'has_breakfast')
    op.drop_column('hotel_visits', 'pool_rating')
    op.drop_column('hotel_visits', 'pool_heated')
    op.drop_column('hotel_visits', 'has_pool')

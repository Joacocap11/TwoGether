"""add optional restaurant and hotel pricing

Revision ID: 0008_pricing
Revises: 0007_user_security
"""
from alembic import op
import sqlalchemy as sa

revision='0008_pricing'
down_revision='0007_user_security'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('place_visits', sa.Column('currency', sa.String(length=3), nullable=True))
    op.add_column('dishes', sa.Column('dish_price', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('dishes', sa.Column('drink_price', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('dishes', sa.Column('dessert_price', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('hotel_visits', sa.Column('total_price', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('hotel_visits', sa.Column('currency', sa.String(length=3), nullable=True))


def downgrade():
    op.drop_column('hotel_visits', 'currency')
    op.drop_column('hotel_visits', 'total_price')
    op.drop_column('dishes', 'dessert_price')
    op.drop_column('dishes', 'drink_price')
    op.drop_column('dishes', 'dish_price')
    op.drop_column('place_visits', 'currency')

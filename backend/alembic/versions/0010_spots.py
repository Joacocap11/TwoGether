"""add spots and spot_ratings

Revision ID: 0010_spots
Revises: 0009_refresh_tokens
"""
from alembic import op
import sqlalchemy as sa

revision = '0010_spots'
down_revision = '0009_refresh_tokens'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('spots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('location', sa.String(300)),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(9)),
        sa.Column('visit_date', sa.Date()),
        sa.Column('notes', sa.Text()),
        sa.Column('image_path', sa.String(500)),
        sa.Column('status', sa.String(8), nullable=False, server_default='WISHLIST'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()))
    op.create_index('ix_spots_name', 'spots', ['name'])
    op.create_table('spot_ratings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text()),
        sa.Column('spot_id', sa.Integer(), sa.ForeignKey('spots.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('spot_id', 'user_id', name='uq_spot_rating_spot_user'))


def downgrade():
    op.drop_table('spot_ratings')
    op.drop_index('ix_spots_name', table_name='spots')
    op.drop_table('spots')

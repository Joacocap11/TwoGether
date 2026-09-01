"""add shared media and hotel visits

Revision ID: 0005_media_hotels
Revises: 0004_place_category
"""
from alembic import op
import sqlalchemy as sa

revision='0005_media_hotels'
down_revision='0004_place_category'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('media_entries',
        sa.Column('id',sa.Integer,primary_key=True), sa.Column('title',sa.String(200),nullable=False),
        sa.Column('media_type',sa.String(6),nullable=False), sa.Column('watched_date',sa.Date,nullable=False),
        sa.Column('category',sa.String(120)), sa.Column('image_path',sa.String(500)),
        sa.Column('created_at',sa.DateTime,server_default=sa.func.now()), sa.Column('updated_at',sa.DateTime,server_default=sa.func.now()))
    op.create_table('media_ratings',
        sa.Column('id',sa.Integer,primary_key=True), sa.Column('media_entry_id',sa.Integer,sa.ForeignKey('media_entries.id'),nullable=False),
        sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id'),nullable=False), sa.Column('score',sa.Float,nullable=False),
        sa.UniqueConstraint('media_entry_id','user_id',name='uq_media_rating_entry_user'))
    op.create_table('hotel_visits',
        sa.Column('id',sa.Integer,primary_key=True), sa.Column('name',sa.String(200),nullable=False),
        sa.Column('visit_date',sa.Date,nullable=False), sa.Column('location',sa.String(300)), sa.Column('image_path',sa.String(500)),
        sa.Column('created_at',sa.DateTime,server_default=sa.func.now()), sa.Column('updated_at',sa.DateTime,server_default=sa.func.now()))
    op.create_table('hotel_ratings',
        sa.Column('id',sa.Integer,primary_key=True), sa.Column('hotel_visit_id',sa.Integer,sa.ForeignKey('hotel_visits.id'),nullable=False),
        sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id'),nullable=False), sa.Column('score',sa.Float,nullable=False),
        sa.Column('opinion',sa.Text), sa.UniqueConstraint('hotel_visit_id','user_id',name='uq_hotel_rating_visit_user'))


def downgrade():
    op.drop_table('hotel_ratings'); op.drop_table('hotel_visits'); op.drop_table('media_ratings'); op.drop_table('media_entries')

"""add per-person hotel amenity ratings

Revision ID: 0012_hotel_amenity_ratings
Revises: 0011_hotel_amenities

pool_rating/breakfast_rating on hotel_visits (added in 0011) were a single
general score, not per-person. Production inspection before writing this
migration found exactly one row with real data (a hotel with pool_rating=6
and breakfast_rating=6, both set together with has_pool/has_breakfast). To
avoid silently destroying that opinion, its score is copied into a
hotel_amenity_ratings row for every existing user (the app is always
exactly two users, Joaco and Selena) for the corresponding amenity, before
the old columns are dropped. Hotels with NULL pool_rating/breakfast_rating
(the common case) produce no rows.
"""
from alembic import op
import sqlalchemy as sa

revision = '0012_hotel_amenity_ratings'
down_revision = '0011_hotel_amenities'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('hotel_amenity_ratings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotel_visits.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('amenity', sa.String(length=9), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('hotel_id', 'user_id', 'amenity', name='uq_hotel_amenity_rating'))

    conn = op.get_bind()
    user_ids = [row[0] for row in conn.execute(sa.text('SELECT id FROM users')).fetchall()]
    for column, amenity in (('pool_rating', 'POOL'), ('breakfast_rating', 'BREAKFAST')):
        rows = conn.execute(sa.text(f'SELECT id, {column} FROM hotel_visits WHERE {column} IS NOT NULL')).fetchall()
        for hotel_id, score in rows:
            for user_id in user_ids:
                conn.execute(
                    sa.text(
                        'INSERT INTO hotel_amenity_ratings (hotel_id, user_id, amenity, score, created_at, updated_at) '
                        'VALUES (:hotel_id, :user_id, :amenity, :score, now(), now())'
                    ),
                    {'hotel_id': hotel_id, 'user_id': user_id, 'amenity': amenity, 'score': score},
                )

    op.drop_column('hotel_visits', 'breakfast_rating')
    op.drop_column('hotel_visits', 'pool_rating')


def downgrade():
    op.add_column('hotel_visits', sa.Column('pool_rating', sa.Integer(), nullable=True))
    op.add_column('hotel_visits', sa.Column('breakfast_rating', sa.Integer(), nullable=True))
    op.drop_table('hotel_amenity_ratings')

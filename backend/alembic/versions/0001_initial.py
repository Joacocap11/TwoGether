"""initial schema"""
from alembic import op
import sqlalchemy as sa
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table('users',sa.Column('id',sa.Integer,primary_key=True),sa.Column('name',sa.String(120),nullable=False),sa.Column('email',sa.String(255),nullable=False,unique=True),sa.Column('hashed_password',sa.String(255),nullable=False),sa.Column('is_active',sa.Boolean,nullable=False,server_default='1'),sa.Column('created_at',sa.DateTime,server_default=sa.func.now()))
    op.create_table('place_visits',sa.Column('id',sa.Integer,primary_key=True),sa.Column('name',sa.String(200),nullable=False),sa.Column('visit_date',sa.Date,nullable=False),sa.Column('location',sa.String(300),nullable=True),sa.Column('notes',sa.Text),sa.Column('image_path',sa.String(500)),sa.Column('created_at',sa.DateTime,server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime,server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime))
    op.create_table('user_ratings',sa.Column('id',sa.Integer,primary_key=True),sa.Column('score',sa.Float,nullable=False),sa.Column('comment',sa.Text),sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id'),nullable=False),sa.Column('visit_id',sa.Integer,sa.ForeignKey('place_visits.id'),nullable=False),sa.Column('created_at',sa.DateTime,server_default=sa.func.now()))
    op.create_table('dishes',sa.Column('id',sa.Integer,primary_key=True),sa.Column('name',sa.String(200),nullable=False),sa.Column('description',sa.Text),sa.Column('image_path',sa.String(500)),sa.Column('visit_id',sa.Integer,sa.ForeignKey('place_visits.id'),nullable=False),sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id')),sa.Column('score',sa.Float,nullable=False),sa.Column('notes',sa.Text),sa.Column('created_at',sa.DateTime,server_default=sa.func.now()))
    op.create_table('test_records',sa.Column('id',sa.Integer,primary_key=True),sa.Column('title',sa.String(200),nullable=False),sa.Column('result',sa.Text,nullable=False),sa.Column('test_date',sa.Date,nullable=False),sa.Column('notes',sa.Text),sa.Column('image_path',sa.String(500)),sa.Column('created_at',sa.DateTime,server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime,server_default=sa.func.now()))
def downgrade():
    for t in ('test_records','dishes','user_ratings','place_visits','users'): op.drop_table(t)

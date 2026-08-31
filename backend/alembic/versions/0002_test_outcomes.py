"""add shared test outcomes"""
from alembic import op
import sqlalchemy as sa
revision='0002_test_outcomes'; down_revision='0001_initial'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('test_outcomes',
        sa.Column('id',sa.Integer,primary_key=True),
        sa.Column('test_record_id',sa.Integer,sa.ForeignKey('test_records.id'),nullable=False),
        sa.Column('user_id',sa.Integer,sa.ForeignKey('users.id'),nullable=False),
        sa.Column('result',sa.Text,nullable=False),
        sa.Column('image_path',sa.String(500)),
        sa.UniqueConstraint('test_record_id','user_id',name='uq_test_outcome_record_user'))

def downgrade():
    op.drop_table('test_outcomes')

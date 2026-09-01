"""allow tests and outcomes without textual results"""
from alembic import op

revision = '0003_nullable_test_results'
down_revision = '0002_test_outcomes'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('test_records') as batch_op:
        batch_op.alter_column('result', nullable=True)
    with op.batch_alter_table('test_outcomes') as batch_op:
        batch_op.alter_column('result', nullable=True)


def downgrade():
    with op.batch_alter_table('test_outcomes') as batch_op:
        batch_op.alter_column('result', nullable=False)
    with op.batch_alter_table('test_records') as batch_op:
        batch_op.alter_column('result', nullable=False)

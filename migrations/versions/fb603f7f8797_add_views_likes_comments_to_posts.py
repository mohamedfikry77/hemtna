"""add views, likes, comments to posts

Revision ID: fb603f7f8797
Revises: f6a5ba0cc73d
Create Date: 2025-06-25 18:18:39.490418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb603f7f8797'
down_revision = 'f6a5ba0cc73d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('views', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('views')

    # ### end Alembic commands ###

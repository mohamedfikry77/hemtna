"""add all user profile fields

Revision ID: c42846f0334d
Revises: 831a32a4c69b
Create Date: 2025-06-24 17:37:40.355180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c42846f0334d'
down_revision = '831a32a4c69b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('last_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('country_code', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('child_birthdate', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('doctor_specialty', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint('uq_user_phone', ['phone'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_phone', type_='unique')
        batch_op.drop_column('doctor_specialty')
        batch_op.drop_column('child_birthdate')
        batch_op.drop_column('country_code')
        batch_op.drop_column('phone')
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    # ### end Alembic commands ###

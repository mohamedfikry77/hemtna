"""rename treatmentplan table to activity and update all references

Revision ID: 682fb8dd509b
Revises: 5c64bc2fd10f
Create Date: 2025-06-25 19:45:56.778450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '682fb8dd509b'
down_revision = '5c64bc2fd10f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('treatment_plan')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('treatment_plan',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('child_name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('doctor_id', sa.INTEGER(), nullable=True),
    sa.Column('parent_id', sa.INTEGER(), nullable=True),
    sa.Column('details', sa.TEXT(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###

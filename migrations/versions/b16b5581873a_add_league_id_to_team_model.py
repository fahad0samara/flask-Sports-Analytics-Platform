"""Add league_id to Team model

Revision ID: b16b5581873a
Revises: c66d2be45182
Create Date: 2024-11-25 13:59:39.111744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b16b5581873a'
down_revision = 'c66d2be45182'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.add_column(sa.Column('country', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('founded_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.alter_column('logo_url',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=256),
               existing_nullable=True)
        batch_op.create_unique_constraint(None, ['name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('logo_url',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
        batch_op.drop_column('description')
        batch_op.drop_column('founded_year')
        batch_op.drop_column('country')

    # ### end Alembic commands ###
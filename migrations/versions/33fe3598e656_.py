"""empty message

Revision ID: 33fe3598e656
Revises: 8c22ca5d2b01
Create Date: 2020-08-17 20:44:28.156959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33fe3598e656'
down_revision = '8c22ca5d2b01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('num_upcoming_shows', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'num_upcoming_shows')
    # ### end Alembic commands ###

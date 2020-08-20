"""empty message

Revision ID: f22a3404d07e
Revises: fabe63471635
Create Date: 2020-08-20 19:24:20.576421

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f22a3404d07e'
down_revision = 'fabe63471635'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('show')


def downgrade():
    pass

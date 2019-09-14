"""update user

Revision ID: 720a10f5ca17
Revises: 8516f33c0deb
Create Date: 2019-08-16 16:09:13.390258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '720a10f5ca17'
down_revision = '8516f33c0deb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_seen')
    op.drop_column('users', 'about_me')
    # ### end Alembic commands ###
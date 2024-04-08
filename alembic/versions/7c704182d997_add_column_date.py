"""Add column date

Revision ID: 7c704182d997
Revises: 147335d7e7e9
Create Date: 2024-04-08 15:33:18.613295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c704182d997'
down_revision: Union[str, None] = '147335d7e7e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('carts', sa.Column('create_date', sa.DateTime(), nullable=True))
    op.add_column('cartsitems', sa.Column('add_date', sa.DateTime(), nullable=True))
    op.add_column('orders', sa.Column('create_date', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('registration_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'registration_date')
    op.drop_column('orders', 'create_date')
    op.drop_column('cartsitems', 'add_date')
    op.drop_column('carts', 'create_date')
    # ### end Alembic commands ###
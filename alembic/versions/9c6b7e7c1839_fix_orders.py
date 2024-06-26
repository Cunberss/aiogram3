"""Fix orders

Revision ID: 9c6b7e7c1839
Revises: e951abdab8eb
Create Date: 2024-04-08 13:35:04.102798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c6b7e7c1839'
down_revision: Union[str, None] = 'e951abdab8eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('address', sa.Text(), nullable=False))
    op.add_column('orders', sa.Column('price', sa.Numeric(), nullable=False))
    op.add_column('orders', sa.Column('products', sa.Text(), nullable=False))
    op.drop_column('orders', 'phone')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('orders', 'products')
    op.drop_column('orders', 'price')
    op.drop_column('orders', 'address')
    # ### end Alembic commands ###

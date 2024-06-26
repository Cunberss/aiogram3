"""Fix orders2

Revision ID: 147335d7e7e9
Revises: 9c6b7e7c1839
Create Date: 2024-04-08 13:39:34.229765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '147335d7e7e9'
down_revision: Union[str, None] = '9c6b7e7c1839'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('status', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'status')
    # ### end Alembic commands ###

"""Initial migration

Revision ID: 1c41c97f94a1
Revises: d0340f2fde37
Create Date: 2024-09-04 09:22:05.728034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c41c97f94a1'
down_revision: Union[str, None] = 'd0340f2fde37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('cve_records', 'state',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('cve_records', 'assigner_short_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('cve_records', 'assigner_short_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('cve_records', 'state',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
"""Initial migration

Revision ID: d0340f2fde37
Revises: 
Create Date: 2024-09-03 21:57:19.507797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0340f2fde37'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cve_records',
    sa.Column('id', sa.String(length=30), nullable=False),
    sa.Column('assigner_org_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.Column('assigner_short_name', sa.String(), nullable=False),
    sa.Column('date_reserved', sa.DateTime(timezone=True), nullable=True),
    sa.Column('date_published', sa.DateTime(timezone=True), nullable=True),
    sa.Column('date_updated', sa.DateTime(timezone=True), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cve_records_id'), 'cve_records', ['id'], unique=False)
    op.create_table('problem_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cve_record_id', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['cve_record_id'], ['cve_records.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_problem_types_id'), 'problem_types', ['id'], unique=False)
    op.create_table('references',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('tags', sa.String(), nullable=False),
    sa.Column('cve_record_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['cve_record_id'], ['cve_records.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_references_id'), 'references', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_references_id'), table_name='references')
    op.drop_table('references')
    op.drop_index(op.f('ix_problem_types_id'), table_name='problem_types')
    op.drop_table('problem_types')
    op.drop_index(op.f('ix_cve_records_id'), table_name='cve_records')
    op.drop_table('cve_records')
    # ### end Alembic commands ###
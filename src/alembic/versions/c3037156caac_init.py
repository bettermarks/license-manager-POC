"""init

Revision ID: c3037156caac
Revises: 
Create Date: 2023-01-21 18:15:16.896607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3037156caac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('license',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_license_id'), 'license', ['id'], unique=False)
    op.create_table('product',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=False)
    op.create_table('user_class_management_provider',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('hierarchy_url', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_class_management_provider_id'), 'user_class_management_provider', ['id'], unique=False)
    op.create_table('hierarchy_level',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('ref_ucm_provider', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('hierarchy_url', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['ref_ucm_provider'], ['user_class_management_provider.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hierarchy_level_id'), 'hierarchy_level', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_hierarchy_level_id'), table_name='hierarchy_level')
    op.drop_table('hierarchy_level')
    op.drop_index(op.f('ix_user_class_management_provider_id'), table_name='user_class_management_provider')
    op.drop_table('user_class_management_provider')
    op.drop_index(op.f('ix_product_id'), table_name='product')
    op.drop_table('product')
    op.drop_index(op.f('ix_license_id'), table_name='license')
    op.drop_table('license')
    # ### end Alembic commands ###

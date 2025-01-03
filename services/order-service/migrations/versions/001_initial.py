"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-03 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('items', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)

    # Create menu_items table
    op.create_table(
        'menu_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('alcohol_content', sa.Float(), nullable=True),
        sa.Column('flavor_profile', sa.JSON(), nullable=True),
        sa.Column('ingredients', sa.JSON(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_menu_items_id'), 'menu_items', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_menu_items_id'), table_name='menu_items')
    op.drop_table('menu_items')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')

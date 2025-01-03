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
    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('channel_name', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('room_type', sa.String(), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('current_participants', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('channel_name')
    )
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)

    # Create room_participants table
    op.create_table(
        'room_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_participants_id'), 'room_participants', ['id'], unique=False)

    # Create room_messages table
    op.create_table(
        'room_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_messages_id'), 'room_messages', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_room_messages_id'), table_name='room_messages')
    op.drop_table('room_messages')
    op.drop_index(op.f('ix_room_participants_id'), table_name='room_participants')
    op.drop_table('room_participants')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_table('rooms')

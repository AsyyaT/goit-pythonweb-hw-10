"""Added user model

Revision ID: 8d52e2904fe6
Revises: 
Create Date: 2025-04-08 17:20:33.892704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d52e2904fe6'
down_revision: Union[str, None] = 'cde56f8c51db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'contacts', 'users', ['owner_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contacts', type_='foreignkey')
    op.drop_column('contacts', 'owner_id')
    # ### end Alembic commands ###

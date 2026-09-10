"""adding phone number column in users table

Revision ID: d5ee66f4fc74
Revises: 
Create Date: 2026-09-01 15:41:37.536709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5ee66f4fc74'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number',sa.String,nullable=True))  # here we are adding a new column 'phone_number' in the 'users' table. The column is of type String and it is nullable.


def downgrade() -> None:
    op.drop_column('users', 'phone_number') # here we are dropping the column 'phone_number' from the 'users' table.

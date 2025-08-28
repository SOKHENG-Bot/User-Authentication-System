"""change session_token to Text

Revision ID: 2b65902ffc4e
Revises: 12e0fd05f2cd
Create Date: 2025-08-28 18:07:33.841819
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b65902ffc4e"
down_revision: Union[str, Sequence[str], None] = "12e0fd05f2cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change column type from String(255) → Text
    op.alter_column(
        "user_sessions",
        "session_token",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert back to String(255)
    op.alter_column(
        "user_sessions",
        "session_token",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

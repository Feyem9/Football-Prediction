"""add_performance_indexes

Revision ID: 6754bd05ce34
Revises: 3992bc3bd010
Create Date: 2026-01-13 06:49:15.983653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6754bd05ce34'
down_revision: Union[str, Sequence[str], None] = '3992bc3bd010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_expert_predictions_confidence'), 'expert_predictions', ['confidence'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_expert_predictions_confidence'), table_name='expert_predictions')

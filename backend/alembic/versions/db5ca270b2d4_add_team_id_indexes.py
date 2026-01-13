"""add_team_id_indexes

Revision ID: db5ca270b2d4
Revises: 6754bd05ce34
Create Date: 2026-01-13 07:32:00.912701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db5ca270b2d4'
down_revision: Union[str, Sequence[str], None] = '6754bd05ce34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_matches_home_team_id'), 'matches', ['home_team_id'], unique=False)
    op.create_index(op.f('ix_matches_away_team_id'), 'matches', ['away_team_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_matches_away_team_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_home_team_id'), table_name='matches')

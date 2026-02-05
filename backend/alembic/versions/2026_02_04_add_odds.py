"""Add odds columns to matches

Revision ID: 2026_02_04_add_odds
Revises: 2026_02_02_precision_journal
Create Date: 2026-02-04 21:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_02_04_add_odds'
down_revision = '2026_02_02_precision_journal'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ajouter les colonnes de cotes de paris
    op.add_column('matches', sa.Column('odds_home', sa.Float(), nullable=True))
    op.add_column('matches', sa.Column('odds_draw', sa.Float(), nullable=True))
    op.add_column('matches', sa.Column('odds_away', sa.Float(), nullable=True))
    op.add_column('matches', sa.Column('odds_updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('matches', 'odds_updated_at')
    op.drop_column('matches', 'odds_away')
    op.drop_column('matches', 'odds_draw')
    op.drop_column('matches', 'odds_home')

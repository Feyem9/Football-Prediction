"""Add precision journal columns

Revision ID: 2026_02_02_precision_journal
Revises: 2026_01_27_apex_analysis
Create Date: 2026-02-02 21:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2026_02_02_precision_journal'
down_revision: Union[str, None] = '2026_01_27_apex_analysis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les colonnes pour le Journal de Précision
    op.add_column('expert_predictions', sa.Column('verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('expert_predictions', sa.Column('winner_correct', sa.Boolean(), nullable=True))
    op.add_column('expert_predictions', sa.Column('score_correct', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('expert_predictions', 'score_correct')
    op.drop_column('expert_predictions', 'winner_correct')
    op.drop_column('expert_predictions', 'verified')

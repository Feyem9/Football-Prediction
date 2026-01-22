"""add important matches fields to predictions

Revision ID: 2026_01_22_add_important_matches
Revises: 2026_01_21_add_3_logics
Create Date: 2026-01-22 01:35:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_01_22_add_important_matches'
down_revision = '2026_01_21_add_3_logics'
branch_labels = None
depends_on = None


def upgrade():
    # Add important matches context columns to expert_predictions
    op.add_column('expert_predictions', sa.Column('home_upcoming_important', sa.String(), nullable=True))
    op.add_column('expert_predictions', sa.Column('home_recent_important', sa.String(), nullable=True))
    op.add_column('expert_predictions', sa.Column('away_upcoming_important', sa.String(), nullable=True))
    op.add_column('expert_predictions', sa.Column('away_recent_important', sa.String(), nullable=True))


def downgrade():
    # Remove columns in reverse order
    op.drop_column('expert_predictions', 'away_recent_important')
    op.drop_column('expert_predictions', 'away_upcoming_important')
    op.drop_column('expert_predictions', 'home_recent_important')
    op.drop_column('expert_predictions', 'home_upcoming_important')

"""add_3_prediction_logics

Revision ID: 2026_01_21_add_3_logics
Revises: 2026_01_16_add_goals_avg
Create Date: 2026-01-21 08:08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_01_21_add_3_logics'
down_revision = 'add_goals_avg_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add Papa logic columns
    op.add_column('expert_predictions', sa.Column('papa_home_score', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('papa_away_score', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('papa_confidence', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('papa_tip', sa.String(), nullable=True))
    
    # Add Grand Frère logic columns
    op.add_column('expert_predictions', sa.Column('grand_frere_home_score', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('grand_frere_away_score', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('grand_frere_confidence', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('grand_frere_tip', sa.String(), nullable=True))
    
    # Add Ma Logique columns
    op.add_column('expert_predictions', sa.Column('ma_logique_home_score', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('ma_logique_away_score', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('ma_logique_confidence', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('ma_logique_tip', sa.String(), nullable=True))


def downgrade():
    # Remove in reverse order
    op.drop_column('expert_predictions', 'ma_logique_tip')
    op.drop_column('expert_predictions', 'ma_logique_confidence')
    op.drop_column('expert_predictions', 'ma_logique_away_score')
    op.drop_column('expert_predictions', 'ma_logique_home_score')
    
    op.drop_column('expert_predictions', 'grand_frere_tip')
    op.drop_column('expert_predictions', 'grand_frere_confidence')
    op.drop_column('expert_predictions', 'grand_frere_away_score')
    op.drop_column('expert_predictions', 'grand_frere_home_score')
    
    op.drop_column('expert_predictions', 'papa_tip')
    op.drop_column('expert_predictions', 'papa_confidence')
    op.drop_column('expert_predictions', 'papa_away_score')
    op.drop_column('expert_predictions', 'papa_home_score')

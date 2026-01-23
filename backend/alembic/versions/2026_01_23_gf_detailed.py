"""add grand frere detailed stats

Revision ID: 2026_01_23_gf_detailed
Revises: 2026_01_22_add_proof_data
Create Date: 2026-01-23 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '2026_01_23_gf_detailed'
down_revision = '2026_01_22_add_proof_data'
branch_labels = None
depends_on = None

def upgrade():
    # H2H detailed stats
    op.add_column('expert_predictions', sa.Column('h2h_matches_count', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('h2h_home_goals_total', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('h2h_away_goals_total', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('h2h_home_goals_freq', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('h2h_away_goals_freq', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('h2h_top_scorer', sa.String(), nullable=True))
    
    # Grand Frère combined analysis
    op.add_column('expert_predictions', sa.Column('gf_home_league_level', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('gf_away_league_level', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('gf_home_advantage_bonus', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('gf_verdict', sa.String(), nullable=True))

def downgrade():
    op.drop_column('expert_predictions', 'gf_verdict')
    op.drop_column('expert_predictions', 'gf_home_advantage_bonus')
    op.drop_column('expert_predictions', 'gf_away_league_level')
    op.drop_column('expert_predictions', 'gf_home_league_level')
    op.drop_column('expert_predictions', 'h2h_top_scorer')
    op.drop_column('expert_predictions', 'h2h_away_goals_freq')
    op.drop_column('expert_predictions', 'h2h_home_goals_freq')
    op.drop_column('expert_predictions', 'h2h_away_goals_total')
    op.drop_column('expert_predictions', 'h2h_home_goals_total')
    op.drop_column('expert_predictions', 'h2h_matches_count')

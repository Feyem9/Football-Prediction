"""add proof data

Revision ID: 2026_01_22_add_proof_data
Revises: 2026_01_22_add_important_matches
Create Date: 2026-01-22 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '2026_01_22_add_proof_data'
down_revision = '2026_01_22_add_important_matches'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('expert_predictions', sa.Column('h2h_home_wins', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('h2h_away_wins', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('h2h_draws', sa.Integer(), nullable=True))
    op.add_column('expert_predictions', sa.Column('home_form_score', sa.Float(), nullable=True))
    op.add_column('expert_predictions', sa.Column('away_form_score', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('expert_predictions', 'away_form_score')
    op.drop_column('expert_predictions', 'home_form_score')
    op.drop_column('expert_predictions', 'h2h_draws')
    op.drop_column('expert_predictions', 'h2h_away_wins')
    op.drop_column('expert_predictions', 'h2h_home_wins')

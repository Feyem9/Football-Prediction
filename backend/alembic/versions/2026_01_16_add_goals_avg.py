"""Add home_goals_avg and away_goals_avg to expert_predictions

Revision ID: add_goals_avg_001
Revises: db5ca270b2d4
Create Date: 2026-01-16
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_goals_avg_001'
down_revision = 'db5ca270b2d4'
branch_labels = None
depends_on = None

def upgrade():
    # Add home_goals_avg and away_goals_avg columns
    op.add_column('expert_predictions', 
        sa.Column('home_goals_avg', sa.Float(), nullable=True, default=0.0)
    )
    op.add_column('expert_predictions', 
        sa.Column('away_goals_avg', sa.Float(), nullable=True, default=0.0)
    )

def downgrade():
    op.drop_column('expert_predictions', 'home_goals_avg')
    op.drop_column('expert_predictions', 'away_goals_avg')

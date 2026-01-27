"""add ma_logique_analysis column

Revision ID: 2026_01_27_add_ma_logique_analysis
Revises: 2026_01_23_gf_detailed
Create Date: 2026-01-27 07:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '2026_01_27_add_ma_logique_analysis'
down_revision = '2026_01_23_gf_detailed'
branch_labels = None
depends_on = None

def upgrade():
    # Ad ma_logique_analysis column to expert_predictions table
    op.add_column('expert_predictions', sa.Column('ma_logique_analysis', sa.String(), nullable=True))

def downgrade():
    op.drop_column('expert_predictions', 'ma_logique_analysis')

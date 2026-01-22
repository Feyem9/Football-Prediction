import os
import sys
from alembic.config import Config
from alembic import command

def run_upgrade():
    # Path to alembic.ini
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(base_dir, "alembic.ini")
    
    # Create Alembic configuration
    alembic_cfg = Config(ini_path)
    
    # Run the upgrade
    print("Applying migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied successfully!")

if __name__ == "__main__":
    run_upgrade()

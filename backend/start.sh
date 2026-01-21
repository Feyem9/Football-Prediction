#!/bin/bash
set -e

echo "🔄 Starting migration process..."

# Check if alembic_version table exists
if psql "$DATABASE_URL" -c "SELECT 1 FROM alembic_version LIMIT 1;" > /dev/null 2>&1; then
    echo "✅ Database already has migration history"
    
    # Get current version
    CURRENT_VERSION=$(psql "$DATABASE_URL" -t -c "SELECT version_num FROM alembic_version;" | xargs)
    echo "📌 Current version: ${CURRENT_VERSION:-none}"
    
    # If no version or old version, stamp to add_goals_avg_001
    if [ -z "$CURRENT_VERSION" ] || [ "$CURRENT_VERSION" = "db5ca270b2d4" ]; then
        echo "⏩ Stamping to add_goals_avg_001 (skipping old migrations)"
        alembic stamp add_goals_avg_001
    fi
else
    echo "🆕 Fresh database, stamping to add_goals_avg_001"
    alembic stamp add_goals_avg_001
fi

# Apply new migrations
echo "🚀 Applying new migrations..."
alembic upgrade head

echo "✅ Migrations complete!"

# Start the server
cd app
exec uvicorn main:app --host 0.0.0.0 --port $PORT

FROM python:3.13-slim

WORKDIR /app

# Dépendances système pour psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render uses PORT env variable
ENV PORT=8000
EXPOSE $PORT

CMD alembic upgrade head && cd app && uvicorn main:app --host 0.0.0.0 --port $PORT

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

# Make start script executable
RUN chmod +x start.sh

# Render uses PORT env variable
ENV PORT=8000
EXPOSE $PORT

CMD ["./start.sh"]

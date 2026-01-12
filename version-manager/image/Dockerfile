FROM python:3.12-slim

WORKDIR /app

# Install curl for downloading libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/*.py .
COPY src/ui/ ./ui/

# Download React libraries
RUN mkdir -p /app/ui/libs && \
    curl -sL https://unpkg.com/react@18/umd/react.production.min.js -o /app/ui/libs/react.production.min.js && \
    curl -sL https://unpkg.com/react-dom@18/umd/react-dom.production.min.js -o /app/ui/libs/react-dom.production.min.js && \
    curl -sL https://unpkg.com/@babel/standalone/babel.min.js -o /app/ui/libs/babel.min.js

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

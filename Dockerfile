FROM python:3.12-slim

# Prevent Python from writing pyc files & buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /code

# System deps needed for psycopg2, blis/spacy builds, etc.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download the small spaCy English model (optional but used by NLP service)
RUN python -m spacy download en_core_web_sm || true

# Copy application code
COPY . .

# Create upload dir
RUN mkdir -p uploads

EXPOSE 8000

# Entrypoint runs migrations then starts the server
CMD ["bash", "scripts/entrypoint.sh"]

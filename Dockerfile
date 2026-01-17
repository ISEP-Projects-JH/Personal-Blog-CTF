FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y \
    mariadb-server \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# python deps
COPY pyproject.toml /app/
RUN pip install --upgrade pip \
    && pip install --no-build-isolation .

# app code
COPY . /app

# run DB bootstrap ONCE at build time
RUN chmod +x docker_scripts/bootstrap_db.sh \
    && bash docker_scripts/bootstrap_db.sh

# runtime entrypoint
COPY docker_scripts/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
CMD ["/entrypoint.sh"]

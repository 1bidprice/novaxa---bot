"""
Deployment configuration for NOVAXA Dashboard and Telegram Bot
"""

import os

# Configuration for different environments
config = {
    "development": {
        "api_url": "http://localhost:5000/api",
        "web_url": "http://localhost:8080",
        "debug": True,
        "webhook_enabled": False
    },
    "production": {
        "api_url": "https://api.novaxa-dashboard.example.com/api",
        "web_url": "https://novaxa-dashboard.example.com",
        "debug": False,
        "webhook_enabled": True,
        "webhook_url": "https://api.novaxa-dashboard.example.com/webhook"
    }
}

# Dockerfile for API
dockerfile_api = """
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .
COPY .env .

EXPOSE 5000

CMD ["python", "api.py"]
"""

# Dockerfile for Web
dockerfile_web = """
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY integration.py .
COPY templates/ templates/
COPY static/ static/
COPY .env .

EXPOSE 8080

CMD ["python", "integration.py"]
"""

# Docker Compose file
docker_compose = """
version: '3'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
    restart: always
    volumes:
      - api_data:/app/data

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
    restart: always
    volumes:
      - web_data:/app/data
"""

# Write Dockerfiles and Docker Compose to files
with open("Dockerfile.api", "w") as f:
    f.write(dockerfile_api)

with open("Dockerfile.web", "w") as f:
    f.write(dockerfile_web)

with open("docker-compose.yml", "w") as f:
    f.write(docker_compose)

print("Deployment configuration files created.")

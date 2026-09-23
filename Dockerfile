# Stage 1: Build the React/Vite Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /build

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Build production bundle
COPY frontend/ ./
RUN npm run build

# Stage 2: Python 3.12 Runtime with Playwright Chromium & Dependencies
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies needed for compiling packages and running Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Install Playwright Chromium and required Linux system dependencies
RUN playwright install --with-deps chromium

# Copy compiled frontend from Stage 1 into /app/frontend/dist
COPY --from=frontend-builder /build/dist ./frontend/dist

# Copy application backend codebase and tests
COPY server.py app.py pytest.ini ./
COPY src/ ./src/
COPY tests/ ./tests/

# Expose default port
EXPOSE 8000

# Start FastAPI with Uvicorn binding to 0.0.0.0 and dynamic $PORT (Render / local)
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]

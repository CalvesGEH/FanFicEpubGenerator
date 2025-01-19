# Use Python slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKERMODE=true
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=100
ENV NAME=RoyalRoadAutomatedDownloader
ENV INGEST_DIR=/cwa-book-ingest
ENV PYTHONPATH=/app

# Default UID and GID (can be overridden at runtime)
ENV UID=1000
ENV GID=100

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start application
CMD ["python", "FanFicEpubGenerator.py"]

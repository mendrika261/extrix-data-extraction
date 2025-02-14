# Use Python 3.10 as base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p tmp/cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CACHE_DIR=/app/tmp/cache

# Default command
ENTRYPOINT ["sh", "-c", "cd /app && python cli.py \"$@\"", "--"]
CMD ["--help"]

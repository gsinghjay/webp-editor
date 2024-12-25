FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    webp \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with correct permissions
RUN mkdir -p /app/static/uploads /app/templates && \
    chmod 777 /app/static/uploads

# Copy application code
COPY app/ .

# Run as non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 
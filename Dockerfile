FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose port (Render will bind to $PORT dynamically, but expose 8000 for local reference)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Start supervisord to launch both Gunicorn and Celery
CMD ["supervisord", "-c", "supervisord.conf"]


FROM python:3.14-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directory (optional - won't fail if files don't exist)
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Run migrations and start server (skip import if data files don't exist)
CMD ["sh", "-c", "python manage.py migrate && python manage.py import_initial_data || true && gunicorn credit_system.wsgi:application --bind 0.0.0.0:8000"]

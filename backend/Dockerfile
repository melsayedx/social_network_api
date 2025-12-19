FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt requirements/dev.txt ./requirements/
RUN pip install -r requirements/dev.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

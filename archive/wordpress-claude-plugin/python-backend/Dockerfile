FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
COPY ../../code-exec.py /app/

# Create a non-root user
RUN useradd -m -u 1000 claude && chown -R claude:claude /app
USER claude

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=claude_backend_server.py
ENV PYTHONUNBUFFERED=1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "claude_backend_server:app"]
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Create virtual environment using uv
RUN uv venv

# Install dependencies using uv pip inside the venv
RUN . .venv/bin/activate && uv pip install --no-cache-dir -r requirements.txt

# Expose port 8080
EXPOSE 8080

# Create data directory with proper permissions
RUN mkdir -p /app/data/runs

# Set environment defaults
ENV FLASK_ENV=production
ENV AGENT_SCHEDULER=true
ENV AGENT_SCHEDULER_TICK_SEC=30

# Ensure venv is used by default
ENV PATH="/app/.venv/bin:$PATH"

# Start the Flask server
CMD ["python", "server.py"]
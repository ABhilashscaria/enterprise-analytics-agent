FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build dependencies (often needed for C-extensions in Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching for layers
COPY requirements.txt .

# Install dependencies (using --no-cache-dir to save disk space!)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

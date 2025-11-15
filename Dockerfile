# AI Stock Agent - Docker deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py .
COPY *.yaml .
COPY *.sh .

# Create necessary directories
RUN mkdir -p /app/charts

# Set environment variables (will be overridden by Railway)
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main_runner.py"]

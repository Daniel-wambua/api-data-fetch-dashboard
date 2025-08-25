# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p /app/cache

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
# Start FastAPI backend in background\n\
uvicorn app:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Wait a moment for backend to start\n\
sleep 5\n\
\n\
# Start Streamlit frontend\n\
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0 --server.headless true\n\
' > /app/start.sh && chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]

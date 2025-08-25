#!/bin/bash

# API Data Dashboard Startup Script
echo "🚀 Starting API Data Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before running again."
    echo "💡 Many features work without API keys, but you'll get better data with them."
    exit 1
fi

# Create cache directory if it doesn't exist
mkdir -p cache

echo "🔥 Starting FastAPI backend..."
uvicorn app:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

echo "📊 Starting Streamlit dashboard..."
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "✅ Dashboard is starting up!"
echo "📊 Streamlit Dashboard: http://localhost:8501"
echo "📖 FastAPI Documentation: http://localhost:8000/docs"
echo "🔌 API Endpoints: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for services
wait

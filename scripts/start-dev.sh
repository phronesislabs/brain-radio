#!/bin/bash
# Development startup script for Brain-Radio

set -e

echo "Starting Brain-Radio Development Environment"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Copying from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "SUCCESS: Created .env file. Please update it with your credentials."
    else
        echo "ERROR: .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Check Python dependencies
echo "Checking Python dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    uv pip install -e ".[dev]"
fi

# Check Node dependencies
echo "Checking Node dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "SUCCESS: Setup complete!"
echo ""
echo "To start the application:"
echo "  Terminal 1 (Backend):  uvicorn src.brain_radio.api.main:app --reload --port 8000"
echo "  Terminal 2 (Frontend):  cd frontend && npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""


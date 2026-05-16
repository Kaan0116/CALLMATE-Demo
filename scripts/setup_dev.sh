#!/usr/bin/env bash
set -e

echo "==> CallMate AI - Development Setup"

cd "$(dirname "$0")/.."

# Backend setup
echo "==> Setting up Python virtual environment..."
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "==> .env created - please edit with your settings"
fi

cd ..

# Frontend setup
echo "==> Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "==> Setup complete!"
echo ""
echo "Start services:"
echo "  docker compose up -d postgres redis qdrant"
echo ""
echo "Run backend:"
echo "  cd backend && source venv/bin/activate && alembic upgrade head && uvicorn app.main:app --reload"
echo ""
echo "Run frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose:"
echo "  docker compose up --build"

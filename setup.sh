#!/bin/bash
# DSAE - Setup Script
# Installs all dependencies for backend and frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=============================="
echo "  DSAE Setup"
echo "=============================="

# --- Backend ---
echo ""
echo "[1/3] Setting up backend..."
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python -m venv venv
fi

echo "  Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "  Installing Python dependencies..."
pip install -r requirements.txt --quiet

# --- Environment file ---
echo ""
echo "[2/3] Checking environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  Created backend/.env from template."
    echo "  >>> Please edit backend/.env and add your API keys. <<<"
else
    echo "  backend/.env already exists."
fi

# --- Frontend ---
echo ""
echo "[3/3] Setting up frontend..."
cd "$SCRIPT_DIR/frontend"

echo "  Installing Node dependencies..."
npm install --silent

# --- Done ---
echo ""
echo "=============================="
echo "  Setup complete!"
echo "=============================="
echo ""
echo "Next steps:"
echo "  1. Add your GEMINI_API_KEY to backend/.env"
echo "  2. Run: ./run.sh"

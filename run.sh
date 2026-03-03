#!/bin/bash
# DSAE - Run Script
# Starts backend (port 9001) and frontend (port 5173)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "=============================="
echo "  DSAE - Starting App"
echo "=============================="

# --- Start Backend ---
echo ""
echo "[Backend] Starting on http://127.0.0.1:9001 ..."
cd "$SCRIPT_DIR/backend"

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

python -m uvicorn app.main:app --host 127.0.0.1 --port 9001 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "[Backend] Waiting for server..."
for i in {1..15}; do
    if curl -s http://127.0.0.1:9001/health > /dev/null 2>&1; then
        echo "[Backend] Ready!"
        break
    fi
    sleep 1
done

# --- Start Frontend ---
echo ""
echo "[Frontend] Starting on http://localhost:5173 ..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=============================="
echo "  App is running!"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://127.0.0.1:9001"
echo "  Press Ctrl+C to stop"
echo "=============================="

wait

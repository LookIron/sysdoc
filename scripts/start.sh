#!/bin/bash

# Start application (frontend + backend)
# Adapt this script to your specific stack

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Load ports from .ports.env if it exists (for worktree isolation)
if [ -f ".ports.env" ]; then
    echo "Loading ports from .ports.env..."
    export $(cat .ports.env | xargs)
fi

FRONTEND_PORT=${FRONTEND_PORT:-5173}
BACKEND_PORT=${BACKEND_PORT:-8000}

echo "Starting application..."
echo "  Frontend port: $FRONTEND_PORT"
echo "  Backend port:  $BACKEND_PORT"

# Kill any existing processes on these ports
for PORT in $FRONTEND_PORT $BACKEND_PORT; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Port $PORT is already in use. Killing existing process..."
        lsof -ti:$PORT | xargs kill -9 || true
        sleep 1
    fi
done

# Start backend
echo "Starting backend on port $BACKEND_PORT..."
cd "$PROJECT_ROOT/app/server"
PORT=$BACKEND_PORT uv run fastapi dev --port $BACKEND_PORT &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on port $FRONTEND_PORT..."
cd "$PROJECT_ROOT/app/client"
PORT=$FRONTEND_PORT bun dev --port $FRONTEND_PORT &
FRONTEND_PID=$!

echo ""
echo "Application started:"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo ""
echo "PIDs: frontend=$FRONTEND_PID backend=$BACKEND_PID"

wait

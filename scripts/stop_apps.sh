#!/bin/bash

# Stop application (frontend + backend)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Load ports from .ports.env if it exists
if [ -f ".ports.env" ]; then
    export $(cat .ports.env | xargs)
fi

FRONTEND_PORT=${FRONTEND_PORT:-5173}
BACKEND_PORT=${BACKEND_PORT:-8000}

echo "Stopping application..."

for PORT in $FRONTEND_PORT $BACKEND_PORT; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Killing process on port $PORT..."
        lsof -ti:$PORT | xargs kill -9 || true
    else
        echo "No process on port $PORT."
    fi
done

echo "All processes stopped."

#!/bin/bash

# Check which ports are in use by the application

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

echo "Checking application ports..."
echo ""

echo "Frontend - Port $FRONTEND_PORT:"
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ✓ Port $FRONTEND_PORT is IN USE"
    lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN
else
    echo "  ✗ Port $FRONTEND_PORT is FREE"
fi

echo ""

echo "Backend - Port $BACKEND_PORT:"
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ✓ Port $BACKEND_PORT is IN USE"
    lsof -Pi :$BACKEND_PORT -sTCP:LISTEN
else
    echo "  ✗ Port $BACKEND_PORT is FREE"
fi

echo ""
echo "Done."

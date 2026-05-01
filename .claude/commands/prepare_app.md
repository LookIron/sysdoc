# Prepare Application

Setup the application for review or testing.

## Variables

PORT: If `.ports.env` exists, read FRONTEND_PORT from it, otherwise default to 5173

## Setup

1. Check if `.ports.env` exists:
   - If it exists, source it and use `FRONTEND_PORT` for the PORT variable
   - If not, use default PORT: 5173

2. Start the application:
   - IMPORTANT: Make sure the server and client are running in a background process using `nohup sh ./scripts/start.sh > /dev/null 2>&1 &`
   - The start.sh script will automatically use ports from `.ports.env` if it exists
   - Use `./scripts/stop_apps.sh` to stop the application

3. Verify the application is running:
   - The application should be accessible at http://localhost:PORT

Note: Read `scripts/` and `README.md` for more information on how to start and stop the application.

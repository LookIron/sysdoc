# Start Application

Start the frontend and backend development servers.

## Instructions

1. Check if `.ports.env` exists to determine the ports
2. If `.ports.env` exists, use `FRONTEND_PORT` and `BACKEND_PORT` from it
3. Otherwise, use defaults: frontend=5173, backend=8000
4. Kill any existing processes on those ports
5. Start both servers

## Implementation

```bash
./scripts/start.sh
```

## Expected Output

```
Starting application...
  Frontend port: 5173
  Backend port:  8000
Starting backend on port 8000...
Starting frontend on port 5173...

Application started:
  Frontend: http://localhost:5173
  Backend:  http://localhost:8000
```

## Ports

- **Frontend default**: 5173
- **Backend default**: 8000
- **Worktree range**: 9000–9029 (read from `.ports.env`)

## Notes

- This command works in both main repo and worktrees
- Worktrees get dedicated ports via `.ports.env`
- Port conflicts are handled automatically

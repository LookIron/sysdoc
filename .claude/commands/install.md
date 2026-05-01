# Install Dependencies

Install all project dependencies (frontend + backend).

## Instructions

1. Install frontend dependencies with bun
2. Install backend dependencies with uv

## Implementation

```bash
# Frontend
cd app/client && bun install

# Backend
cd app/server && uv sync --all-extras
```

## Notes

- Frontend uses bun as package manager
- Backend uses uv as package manager
- For worktree setup, use `/install_worktree` instead

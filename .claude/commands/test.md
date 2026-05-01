# Test

Run all unit tests (frontend + backend).

## Instructions

Run frontend and backend tests and report results.

## Implementation

```bash
# Backend unit tests
cd app/server && uv run pytest

# Frontend type check
cd app/client && bun tsc --noEmit

# Frontend unit tests (if configured)
cd app/client && bun test
```

## Report

Report any test failures with file paths and error messages.

# {PROJECT_NAME}

{PROJECT_DESCRIPTION}

## Facts

| Key | Value |
|-----|-------|
| Frontend port (default) | 5173 |
| Backend port (default) | 8000 |
| Worktree port range | 9000–9029 |
| Frontend start | `cd app/client && bun dev` |
| Backend start | `cd app/server && uv run fastapi dev` |
| Frontend test | `cd app/client && bun test` |
| Backend test | `cd app/server && uv run pytest` |
| Package manager (frontend) | bun |
| Package manager (backend) | uv |
| ADW output | `agents/{adw_id}/` |
| Worktrees | `trees/{adw_id}/` |
| Specs | `specs/` |

## Architecture

```
{PROJECT_NAME}/
├── app/
│   ├── client/      # Frontend (React + TypeScript + Vite)
│   └── server/      # Backend (Python + FastAPI + uv)
├── adws/            # AI Developer Workflow system
├── .claude/         # Claude Code configuration
│   ├── commands/    # Custom slash commands (~30)
│   └── hooks/       # Event hooks
├── scripts/         # Utility shell scripts
├── specs/           # ADW-generated feature specs
├── agents/          # ADW workflow output
├── trees/           # Git worktrees (isolated)
├── ai_docs/         # LLM/API reference docs
└── app_docs/        # Feature documentation + KPIs
```

## Commands

### Development
- `/start` — Start frontend + backend dev servers
- `/install` — Install all dependencies
- `/health_check` — Verify system status
- `/test` — Run unit tests
- `/test_e2e` — Run E2E tests

### Planning
- `/feature` — Plan a new feature
- `/bug` — Plan a bug fix
- `/chore` — Plan maintenance work
- `/patch` — Quick patch

### Implementation
- `/implement <plan-path>` — Implement a plan
- `/review` — Review current work
- `/document` — Generate documentation

### Git & GitHub
- `/commit` — Create a commit
- `/pull_request` — Create a pull request
- `/generate_branch_name` — Generate branch name

### ADW Workflows
- `/classify_issue` — Classify a GitHub issue
- `/classify_adw` — Select ADW workflow for an issue
- `/track_agentic_kpis` — Update ADW KPI metrics

## Conventions

- Branch format: `{issue-class}-issue-{number}-adw-{adw-id}-{description}`
- Commit format: `{agent}: {type}: {message}`
- Plan files: `specs/issue-{number}-adw-{adw-id}-sdlc_planner-{name}.md`
- All ADW output goes to `agents/{adw_id}/`
- Never force push to main

## Environment Variables

See `.env.sample` for required environment variables.

## ADW System

This project uses the **AI Developer Workflow (ADW) System** for automated development.
See `AGENTIC_CODING.md` for full ADW documentation.

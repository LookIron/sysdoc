# SysDoc

El doctor para tu computador. Web app cross-platform (Windows/Mac/Linux) que diagnostica por qué un equipo está lento, detecta problemas de hardware/seguridad/drivers, y permite ejecutar correcciones con un click — con explicaciones en lenguaje humano via Claude AI.

## Facts

| Key | Value |
|-----|-------|
| Frontend port (default) | 5173 |
| Backend port (default) | 8000 |
| Agent debug | `cd app/agent && uv run python main.py --debug` |
| Worktree port range | 9000–9029 |
| Frontend start | `cd app/client && bun dev` |
| Backend start | `cd app/server && uv run fastapi dev` |
| Frontend test | `cd app/client && bun tsc --noEmit` |
| Backend test | `cd app/server && uv run pytest` |
| Agent test | `cd app/agent && uv run pytest` |
| Package manager (frontend) | bun |
| Package manager (backend/agent) | uv |
| API docs | http://localhost:8000/docs |
| Database | Supabase (PostgreSQL free tier) |
| Deploy frontend | Vercel |
| Deploy backend | Railway |
| ADW output | `agents/{adw_id}/` |
| Worktrees | `trees/{adw_id}/` |
| Full spec | `INIT.md` |

## Architecture

```
sysdoc/
├── app/
│   ├── client/      # React + TypeScript + Vite + Tailwind + shadcn/ui + Recharts
│   ├── server/      # Python + FastAPI + Supabase + Claude AI
│   └── agent/       # Python + psutil (daemon local cross-platform)
├── adws/            # AI Developer Workflow system (no tocar)
├── .claude/         # Claude Code configuration
├── scripts/         # Utility shell scripts
└── INIT.md          # Spec completo: arquitectura, DB, API, fases
```

## Domain model

- **Machine** — equipo registrado (hostname, OS, CPU, RAM total)
- **Scan** — snapshot completo con Health Score (0–100) y sub-scores
- **Issue** — problema detectado (código P01–P10), severidad, fix disponible
- **Metric** — serie de tiempo (CPU temp, RAM, disk speed, net)
- **FixHistory** — historial de correcciones aplicadas con resultado

## Health Score

| Sub-score | Qué mide |
|-----------|---------|
| Performance | CPU throttling, memory leaks, background hogs |
| Storage | Disco lleno, SMART, SSD wear, fragmentación |
| Security | Firewall, updates pendientes, procesos sospechosos |
| Stability | Crashes, drivers corruptos, startup fantasmas |

## Issue codes MVP (P01–P10)

| Code | Problema |
|------|---------|
| P01 | Thermal throttling — CPU lento por temperatura |
| P02 | HDD sectores pendientes (SMART C5/C4 > 0) |
| P03 | Memory leak activo (proceso >150% RAM en sesión) |
| P04 | Startup fantasmas (binario no existe) |
| P05 | SSD desgaste >85% o disco >90% lleno |
| P06 | Drivers críticos desactualizados (GPU, NVMe) |
| P07 | Cloud sync en loop (OneDrive/Drive/Dropbox) |
| P08 | Windows Update en background |
| P09 | Antivirus escaneando silenciosamente |
| P10 | Fragmentación severa / TRIM desactivado |

## Key files (post-scaffolding)

- `INIT.md` — Spec completo con DB schema y API endpoints
- `app/server/services/analyzer.py` — Detección de issues P01–P10
- `app/server/services/scorer.py` — Cálculo del Health Score
- `app/server/services/ai_explainer.py` — Claude root cause analysis
- `app/agent/collectors/` — Colectores de métricas por categoría
- `app/agent/fixers/` — Ejecutores de correcciones

## Commands

- `/start` — Start frontend + backend
- `/install` — Install all dependencies
- `/health_check` — Verify ADW system
- `/feature` — Plan a new feature
- `/bug` — Plan a bug fix
- `/implement <plan>` — Implement a plan
- `/test` — Run unit tests
- `/commit` — Create a commit
- `/pull_request` — Create a PR

## Conventions

- Branch: `{type}-issue-{number}-adw-{adw-id}-{description}`
- Commit: `{agent}: {type}: {message}`
- Todos los fixes son reversibles y requieren confirmación explícita del usuario
- Nunca ejecutar operaciones destructivas sin consentimiento del usuario
- Never force push to main

## Environment Variables

Ver `.env.sample`. Servicios requeridos: Supabase (DB+Auth), Anthropic API (Claude AI).

## ADW System

Ver `AGENTIC_CODING.md` para documentación completa del sistema ADW.

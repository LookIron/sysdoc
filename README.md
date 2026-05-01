# base-app-template

A production-ready project template built around the **AI Developer Workflow (ADW) System** — an automated development pipeline that uses Claude Code to plan, implement, test, review, document, and ship features in fully isolated git worktrees.

Clone this template, run `/init-project`, and you have a complete agentic coding environment for any new project without rebuilding the infrastructure from scratch.

---

## What's inside

### Layer 1: ADW System (`adws/`)
The core engine. A Python-based orchestration system that runs Claude Code agents autonomously through the full software development lifecycle.

```
adws/
├── adw_modules/         # Core modules: agent, git, github, state, worktree, etc.
├── adw_workflows/       # Individual stages: plan, build, test, review, document, ship
├── adw_workflows_combined/ # Full pipelines: sdlc, zte, plan+build, etc.
├── adw_triggers/        # Automation triggers: cron polling, webhook server
└── adw_tests/           # ADW system health checks and tests
```

**100% app-agnostic.** Copy as-is to any project.

### Layer 2: Claude Code Configuration (`.claude/`)
27 custom slash commands + 7 event hooks that wire Claude Code into every stage of development.

```
.claude/
├── commands/            # /feature, /bug, /implement, /review, /commit, /pr, ...
├── hooks/               # Pre/post tool use, compaction, notifications, logging
└── settings.json        # Permissions allowlist + hook bindings
```

**Commands copy as-is.** Only `/start`, `/install`, `/test` need stack-specific adaptation.

### Layer 3: Scripts (`scripts/`)
Shell utilities for process management, port allocation, GitHub ops, and tunneling.

```
scripts/
├── start.sh / stop_apps.sh     # Start/stop frontend + backend
├── check_ports.sh               # Port status
├── purge_tree.sh                # Clean up old worktrees
├── expose_webhook.sh            # Cloudflare tunnel for webhooks
└── delete_pr.sh / clear_issue_comments.sh / kill_trigger_webhook.sh
```

### Layer 4: Documentation (`ai_docs/`, `CLAUDE.md`, `AGENTIC_CODING.md`)
Reference docs for LLM APIs + a `CLAUDE.md` with a **Facts table** that gives Claude Code instant context without re-discovering project basics every session (saves ~3–5k tokens per session).

### Layer 5: App Scaffold (`app/`)
Empty placeholder directories for your actual application code.

```
app/
├── client/    # Frontend (default: React + TypeScript + Vite)
└── server/    # Backend (default: Python + FastAPI)
```

---

## Default stack

| Layer | Technology | Package manager | Port |
|-------|-----------|----------------|------|
| Frontend | React + TypeScript + Vite | bun | 5173 |
| Backend | Python + FastAPI | uv | 8000 |
| E2E tests | Playwright | — | — |

The ADW system and Claude commands work with any stack — only the `scripts/` and a few commands need updating when you change frameworks.

---

## How to use this template

### 1. Clone and initialize

```bash
# Clone the template
git clone https://github.com/LookIron/base-app-template my-new-project
cd my-new-project

# Re-initialize git (clean history)
rm -rf .git && git init

# Open in Claude Code
claude .
```

### 2. Run `/init-project`

```
/init-project
```

This command walks you through:
- Setting the project name and description
- Updating `CLAUDE.md`, `README.md`, and `.env.sample`
- Configuring the git remote
- Optionally scaffolding the app skeleton (bun create vite + uv init)
- Running the ADW health check

### 3. Start developing

```bash
/install       # Install dependencies
/start         # Start frontend + backend
/health_check  # Verify everything is ready
```

### 4. Use the ADW system

```bash
# Create a GitHub issue, then run the full SDLC automatically:
gh issue create --title "Add user authentication" --body "..."

python3 adws/adw_sdlc_zte_iso.py --issue-number 1 --model-set base
# Automatically: plans → implements → tests → reviews → documents → creates PR
```

---

## Claude Code Commands

### Development
| Command | Description |
|---------|-------------|
| `/prime` | Load project context (token-optimized) |
| `/start` | Start dev servers |
| `/install` | Install all dependencies |
| `/health_check` | Verify ADW system status |
| `/test` | Run unit tests |
| `/test_e2e` | Run E2E tests |

### Planning
| Command | Description |
|---------|-------------|
| `/feature` | Plan a new feature from a GitHub issue |
| `/bug` | Plan a bug fix |
| `/chore` | Plan maintenance work |
| `/patch` | Quick targeted patch |
| `/classify_issue` | Classify a GitHub issue by type |

### Implementation
| Command | Description |
|---------|-------------|
| `/implement <plan-path>` | Implement an existing plan |
| `/review` | Review current work |
| `/document` | Generate feature documentation |
| `/resolve_failed_test` | Fix a failing unit test |
| `/resolve_failed_e2e_test` | Fix a failing E2E test |
| `/resolve_conflicts` | Resolve merge conflicts |

### Git & GitHub
| Command | Description |
|---------|-------------|
| `/commit` | Create a formatted commit |
| `/pull_request` | Create a pull request |
| `/generate_branch_name` | Generate a branch name |
| `/track_agentic_kpis` | Update ADW performance metrics |

### Template Setup
| Command | Description |
|---------|-------------|
| `/init_project` | Initialize a new project from this template |

---

## ADW Workflows

### Individual stages
```bash
python3 adws/adw_plan_iso.py --issue-number 1
python3 adws/adw_build_iso.py --issue-number 1 --adw-id <id>
python3 adws/adw_test_iso.py --issue-number 1 --adw-id <id>
python3 adws/adw_review_iso.py --issue-number 1 --adw-id <id>
python3 adws/adw_ship_iso.py --issue-number 1 --adw-id <id>
```

### Combined pipelines
```bash
# Plan + Build + Test + Review (most common)
python3 adws/adw_plan_build_test_review_iso.py --issue-number 1 --model-set base

# Full SDLC (all stages)
python3 adws/adw_sdlc_iso.py --issue-number 1 --model-set base

# Zero-touch execution (full SDLC + auto-merge)
python3 adws/adw_sdlc_zte_iso.py --issue-number 1 --model-set base
```

### Automation triggers
```bash
# Poll GitHub issues automatically (every 20s)
python3 adws/adw_triggers/trigger_cron.py --workflow sdlc_zte --model-set base

# Webhook server for GitHub events
python3 adws/adw_triggers/trigger_webhook.py --port 8001 --workflow sdlc_zte
./scripts/expose_webhook.sh   # Expose via Cloudflare Tunnel
```

### Model sets

| Set | Planner | Implementor | Tester | Reviewer | Documenter |
|-----|---------|-------------|--------|----------|------------|
| `opus` | Opus 4.7 | Opus 4.7 | Opus 4.7 | Opus 4.7 | Opus 4.7 |
| `base` | Opus 4.7 | Sonnet 4.6 | Sonnet 4.6 | Sonnet 4.6 | Haiku 4.5 |
| `sonnet` | Sonnet 4.6 | Sonnet 4.6 | Sonnet 4.6 | Sonnet 4.6 | Sonnet 4.6 |

---

## Worktree isolation

Each ADW workflow runs in a fully isolated git worktree with its own port:

```
trees/{adw_id}/    # Isolated copy of the repo
agents/{adw_id}/   # Workflow output (plans, logs, state)
```

- Supports up to 15 concurrent workflows
- Each gets dedicated ports (9000–9029)
- Clean up with `./scripts/purge_tree.sh`

---

## Environment variables

```bash
cp .env.sample .env
# Required for ADW:
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...          # Or set via gh auth login
```

See `.env.sample` for all available variables.

---

## Project structure after `/init-project`

```
my-new-project/
├── app/
│   ├── client/          # Your frontend code
│   └── server/          # Your backend code
├── adws/                # ADW system (untouched)
├── .claude/
│   ├── commands/        # Slash commands
│   └── hooks/           # Event hooks
├── scripts/             # Utility scripts
├── specs/               # ADW-generated feature plans
├── agents/              # ADW workflow output
├── trees/               # Isolated worktrees
├── ai_docs/             # LLM reference docs
├── app_docs/            # Feature docs + KPI metrics
├── CLAUDE.md            # Project facts + architecture
└── AGENTIC_CODING.md    # Full ADW guide
```

---

## Token optimization

This template is designed to minimize Claude Code token usage per session:

- **`CLAUDE.md` Facts table** — Key facts (ports, commands, conventions) in one scannable table. Claude doesn't re-discover them on every `/prime`.
- **`/prime` is minimal** — Only loads `README.md` + `CLAUDE.md` + `conditional_docs.md`. Doesn't load the full ADW docs unless needed.
- **`/conditional_docs` skeleton** — Loads feature-specific docs only when relevant. Grows with the project as you document features.

---

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) — `npm install -g @anthropic-ai/claude-code`
- [uv](https://docs.astral.sh/uv/) — Python package manager
- [bun](https://bun.sh) — JavaScript runtime and package manager
- [gh](https://cli.github.com) — GitHub CLI
- Python 3.10+

---

*Built on the ADW system originally developed for [TruthSeed PWA](https://github.com/LookIron/truthseed-app).*

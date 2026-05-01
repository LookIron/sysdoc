# Initialize New Project from Template

Adapt this template to a new project by updating all placeholder values with real project information.

## Instructions

You are setting up a new project from the base-app-template. Follow each step in order.

### Step 1: Gather project information

Ask the user (or extract from arguments) the following:
- **Project name** (e.g., `my-saas-app`) — used for directory names, titles, package names
- **Project description** — one sentence describing what the app does
- **GitHub repository URL** (e.g., `https://github.com/user/repo`) — optional, can be added later
- **Stack preference**: 
  - Default: React + TypeScript + Vite (frontend) / Python + FastAPI (backend)
  - Alternative: Next.js only / Express + React / other

### Step 2: Update CLAUDE.md

Replace placeholder values in `CLAUDE.md`:
- `{PROJECT_NAME}` → actual project name
- `{PROJECT_DESCRIPTION}` → actual description
- Update the Facts table if using a different stack (ports, commands, package managers)

### Step 3: Update README.md

Replace placeholder values in `README.md`:
- `{PROJECT_NAME}` → actual project name
- `{PROJECT_DESCRIPTION}` → actual description
- `{GITHUB_URL}` → GitHub URL (if provided)
- Update stack-specific setup instructions

### Step 4: Update .env.sample

Add project-specific environment variables to `.env.sample`. At minimum:
```
# Application
NODE_ENV=development

# Backend
BACKEND_PORT=8000

# Frontend
VITE_API_URL=http://localhost:8000
```

### Step 5: Configure git remote (if GitHub URL provided)

```bash
git remote add origin {GITHUB_URL}
```

### Step 6: Adapt scripts for chosen stack

If using a stack different from the default (React + FastAPI), update:
- `scripts/start.sh` — change start commands for your framework
- `scripts/stop_apps.sh` — adjust port defaults if needed
- `.claude/commands/start.md` — update expected output
- `.claude/commands/install.md` — update install commands
- `.claude/commands/test.md` — update test commands

### Step 7: Update AGENTIC_CODING.md

Replace `{PROJECT_NAME}` with the actual project name.

### Step 8: Create initial app structure

If the app directory doesn't have content yet, scaffold the basics:

For React + Vite frontend:
```bash
cd app/client
bun create vite . --template react-ts
bun install
```

For Python + FastAPI backend:
```bash
cd app/server
uv init
uv add fastapi uvicorn
```

(Skip this step if the user wants to scaffold manually.)

### Step 9: Verify ADW system

Run the health check to confirm the ADW system is ready:
```bash
uv run adws/adw_tests/health_check.py
```

### Step 10: Initial commit

```bash
git add -A
git commit -m "feat: initialize {project-name} from base-app-template"
```

## Report

Summarize:
- Project name and description set
- Files updated (list them)
- Stack configuration
- GitHub remote configured (yes/no)
- ADW health check result
- Next steps for the user (what to build first)

## Notes

- The ADW system in `adws/` works out of the box — no changes needed
- All Claude commands in `.claude/commands/` work with any stack
- The `conditional_docs.md` command is intentionally empty — add entries as you document features
- For CI/CD, the GitHub Actions workflow can be added later

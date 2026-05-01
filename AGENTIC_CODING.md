# {PROJECT_NAME} - Agentic Coding Guide

## Overview

Este proyecto utiliza el **AI Developer Workflow (ADW) System**, un sistema de desarrollo automatizado que permite crear, probar, revisar y desplegar features completamente aisladas mediante git worktrees y Claude Code CLI.

## Arquitectura del Sistema

```
{project-name}/
├── adws/                        # AI Developer Workflow System
│   ├── adw_modules/             # Módulos reutilizables
│   ├── adw_workflows/           # Workflows individuales
│   ├── adw_workflows_combined/  # Workflows encadenados
│   ├── adw_triggers/            # Triggers (webhook, cron)
│   ├── adw_tests/               # Tests del sistema ADW
│   └── README.md                # Documentación completa
├── .claude/                     # Claude Code configuration
│   ├── settings.json            # Permisos y hooks
│   ├── commands/                # Comandos personalizados (~30)
│   └── hooks/                   # Hooks de eventos
├── scripts/                     # Shell scripts de utilidad
├── app/
│   ├── client/                  # Frontend
│   └── server/                  # Backend
├── agents/                      # Output de workflows ADW
├── trees/                       # Git worktrees aislados
└── specs/                       # Especificaciones de features
```

## Comandos Principales

### Desarrollo Local

```bash
/start          # Iniciar aplicación
/install        # Instalar dependencias
/health_check   # Verificar estado
/test           # Ejecutar unit tests
/test_e2e       # Ejecutar E2E tests
```

### Planificación de Features

```bash
/feature        # Planificar una nueva feature
/bug            # Planificar un bug fix
/chore          # Planificar mantenimiento
/classify_issue # Clasificar un issue
```

### Implementación

```bash
/implement      # Implementar un plan
/patch          # Patch rápido
/review         # Revisar trabajo
/document       # Generar documentación
```

### Git y GitHub

```bash
/commit             # Crear commit
/pull_request       # Crear pull request
/generate_branch_name # Generar nombre de rama
```

## AI Developer Workflows (ADW)

### Workflows Individuales

| Workflow | Comando                                     | Descripción                 |
| -------- | ------------------------------------------- | --------------------------- |
| Plan     | `python3 adws/adw_workflows/adw_plan_iso.py`     | Crea worktree y genera plan |
| Patch    | `python3 adws/adw_workflows/adw_patch_iso.py`    | Patch rápido aislado        |
| Build    | `python3 adws/adw_workflows/adw_build_iso.py`    | Implementa en worktree      |
| Test     | `python3 adws/adw_workflows/adw_test_iso.py`     | Ejecuta tests aislados      |
| Review   | `python3 adws/adw_workflows/adw_review_iso.py`   | Revisa con screenshots      |
| Document | `python3 adws/adw_workflows/adw_document_iso.py` | Genera docs                 |
| Ship     | `python3 adws/adw_workflows/adw_ship_iso.py`     | Aprueba y mergea PR         |

### Workflows Combinados

| Workflow                                               | Descripción                  |
| ------------------------------------------------------ | ---------------------------- |
| `adw_workflows_combined/adw_plan_build_iso.py`             | Plan + Build                 |
| `adw_workflows_combined/adw_plan_build_test_iso.py`        | Plan + Build + Test          |
| `adw_workflows_combined/adw_plan_build_test_review_iso.py` | Plan + Build + Test + Review |
| `adw_workflows_combined/adw_plan_build_review_iso.py`      | Plan + Build + Review        |
| `adw_workflows_combined/adw_plan_build_document_iso.py`    | Plan + Build + Document      |
| `adw_workflows_combined/adw_sdlc_iso.py`                   | SDLC completo                |
| `adw_workflows_combined/adw_sdlc_zte_iso.py`               | SDLC con auto-merge          |

### Ejemplo de Uso

```bash
# 1. Crear issue en GitHub
gh issue create --title "Add dark mode toggle" --body "..."

# 2. Ejecutar SDLC completo
python3 adws/adw_workflows_combined/adw_sdlc_iso.py \
  --issue-number 123 \
  --model-set base

# 3. El sistema automáticamente:
#    - Crea worktree aislado
#    - Genera plan
#    - Implementa feature
#    - Ejecuta tests
#    - Revisa con screenshots
#    - Crea PR en GitHub
```

## Aislamiento de Worktrees

Cada workflow obtiene:

- **ADW ID único**: 8 caracteres hex (ej: `a1b2c3d4`)
- **Worktree aislado**: `trees/{adw_id}/`
- **Puertos dedicados**: 9000–9029 (soporta 15 instancias concurrentes)
- **State file**: `agents/{adw_id}/adw_state.json`

```bash
./scripts/check_ports.sh   # Verificar puertos en uso
./scripts/purge_tree.sh    # Limpiar worktrees antiguos
```

## Triggers de Automatización

### Polling (Cron)

```bash
python3 adws/adw_triggers/trigger_cron.py \
  --workflow sdlc_zte \
  --model-set base
```

### Webhook

```bash
python3 adws/adw_triggers/trigger_webhook.py \
  --workflow sdlc_zte \
  --model-set base \
  --port 8001

./scripts/expose_webhook.sh  # Exponer vía Cloudflare Tunnel
```

## Estructura de Output

```
agents/{adw_id}/
├── adw_state.json                  # Estado del workflow
├── {adw_id}_plan_spec.md           # Plan especificación
├── planner/raw_output.jsonl        # Output del planner
├── implementor/raw_output.jsonl    # Output del implementador
├── tester/raw_output.jsonl         # Output del tester
├── reviewer/raw_output.jsonl       # Output del reviewer
└── documenter/raw_output.jsonl     # Output del documentador
```

## Model Sets

| Set     | Planner   | Implementor | Tester    | Reviewer  | Documentador |
| ------- | --------- | ----------- | --------- | --------- | ------------ |
| `opus`  | Opus 4.7  | Opus 4.7    | Opus 4.7  | Opus 4.7  | Opus 4.7     |
| `base`  | Opus 4.7  | Sonnet 4.6  | Sonnet 4.6 | Sonnet 4.6 | Haiku 4.5   |
| `sonnet`| Sonnet 4.6| Sonnet 4.6  | Sonnet 4.6| Sonnet 4.6| Sonnet 4.6   |

## Variables de Entorno

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Requerida
GITHUB_PAT=ghp_...              # Para operaciones GitHub
CLAUDE_CODE_PATH=claude         # Path a Claude CLI
E2B_API_KEY=...                 # Agent sandbox (opcional)
CLOUDFLARE_R2_*=...             # Para uploads de screenshots (opcional)
```

## Hooks de Claude Code

| Hook                    | Evento                        |
| ----------------------- | ----------------------------- |
| `pre_tool_use.py`       | Antes de ejecutar herramienta |
| `post_tool_use.py`      | Después de ejecutar           |
| `pre_compact.py`        | Antes de compactar sesión     |
| `user_prompt_submit.py` | Al enviar prompt              |
| `stop.py`               | Al detener sesión             |
| `subagent_stop.py`      | Al detener subagente          |
| `notification.py`       | Notificaciones                |

## Mejores Prácticas

1. Usar workflows completos (`sdlc_iso.py`) para features grandes
2. Usar patches (`adw_patch_iso.py`) para cambios pequeños
3. Siempre ejecutar tests antes de mergear
4. Revisar screenshots del reviewer antes de aprobar
5. Usar model set `opus` para features críticas, `base` para balance costo/calidad
6. Verificar puertos antes de crear nuevo worktree

## Documentación Adicional

- **ADW System**: `adws/README.md`
- **API Reference**: `ai_docs/claude_code_cli_reference.md`
- **Comandos**: `.claude/commands/`
- **Features documentadas**: `app_docs/`

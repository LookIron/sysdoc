# SysDoc — Project Specification

> **El doctor para tu computador.** Una web app que escanea cualquier dispositivo (Windows, Mac, Linux), diagnostica por qué está lento, detecta problemas de seguridad y hardware, y permite ejecutar correcciones con un click — con explicaciones en lenguaje humano potenciadas por IA.

---

## Por qué existe SysDoc

El mercado de herramientas de diagnóstico está fragmentado entre dos mundos que nadie conecta:
- **Herramientas para técnicos** (HWiNFO, Process Monitor): datos perfectos, ilegibles para el 95% de usuarios
- **Herramientas para consumidores** (CCleaner, CleanMyMac): UX aceptable, diagnóstico superficial, sin IA, cada una solo para un OS

**Nadie tiene:** profundidad técnica + lenguaje humano + cross-platform + fixes automáticos + dashboard web moderno.

SysDoc ocupa ese espacio vacío.

---

## Visión del producto

Un usuario instala el agente SysDoc en su computador en 30 segundos. Abre el dashboard web, ve un Health Score de 0 a 100, y en lenguaje simple entiende exactamente por qué su equipo está lento. Con un click aplica las correcciones seguras. El sistema registra métricas históricas para detectar degradación antes de que sea un problema grave.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Usuario                                   │
│                    Dashboard Web (Vercel)                        │
│              React + TypeScript + Vite + Tailwind                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS REST / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                    Backend API (Railway)                          │
│                    Python + FastAPI                               │
│              Claude AI integration (root cause)                  │
│                  Auth via Supabase JWT                            │
└──────────┬───────────────────────────┬───────────────────────────┘
           │ PostgreSQL                │ HTTP polling
┌──────────▼──────────┐   ┌───────────▼───────────────────────────┐
│  Supabase (free)     │   │         Agente Local (~5MB)            │
│  PostgreSQL 500MB    │   │    Python (psutil + platform APIs)     │
│  Auth + Real-time    │   │    Windows / Mac / Linux               │
└─────────────────────┘   │    Recolecta métricas, ejecuta fixes   │
                           └───────────────────────────────────────┘
```

### Flujo de datos
1. El agente corre en la máquina del usuario (daemon ligero)
2. Cada 30 segundos envía métricas al backend (polling o push)
3. El backend analiza, detecta anomalías, llama a Claude para root cause
4. El dashboard web muestra resultados en tiempo real
5. El usuario ve un issue → click "Fix" → backend envía comando al agente → agente ejecuta → confirma

---

## Stack técnico

### Frontend (`app/client/`)
| Tecnología | Versión | Razón |
|-----------|---------|-------|
| React | 18 | Ecosistema, compatibilidad |
| TypeScript | 5 | Type safety |
| Vite | 5 | Build rápido |
| Tailwind CSS | 3 | Utilidades, DX excelente |
| shadcn/ui | latest | Componentes accesibles, sin opinión de estilo |
| Recharts | 2 | Gráficas declarativas en React |
| TanStack Query | 5 | Server state, cache, real-time |
| TanStack Router | 1 | Type-safe routing |
| Zustand | 4 | Client state mínimo |
| Bun | latest | Package manager + runtime |

### Backend (`app/server/`)
| Tecnología | Versión | Razón |
|-----------|---------|-------|
| Python | 3.12 | psutil, cross-platform APIs |
| FastAPI | 0.115 | Async, OpenAPI auto-generado |
| Supabase-py | 2 | DB + Auth client |
| Anthropic SDK | 0.40 | Claude AI para root cause |
| psutil | 6 | Cross-platform system metrics |
| APScheduler | 3 | Jobs periódicos de análisis |
| uv | latest | Package manager |
| pytest | 8 | Testing |

### Agente (`app/agent/`)
| Tecnología | Razón |
|-----------|-------|
| Python + psutil | Cross-platform, cubre Win/Mac/Linux |
| PyInstaller | Empaquetar como .exe/.app/bin sin dependencias |
| httpx | HTTP async para comunicación con backend |
| wmi (Windows) | Drivers, WMI queries, Event Log |
| pyobjc (Mac) | APIs nativas macOS |
| platform/subprocess | Linux /proc, lm-sensors |

### Infraestructura (free tier)
| Servicio | Plan | Límite gratuito | Uso |
|---------|------|----------------|-----|
| **Vercel** | Hobby | Ilimitado | Frontend |
| **Railway** | Trial | $5 crédito/mes (~500h) | Backend FastAPI |
| **Supabase** | Free | 500MB PostgreSQL, 50k users | DB + Auth |

---

## Features — MVP (Fase 1)

### 1. Health Score (0–100)
- Score general visible en la landing del dashboard
- Sub-scores: Performance / Storage / Security / Stability
- Badge de color: Verde (80+) / Amarillo (50-79) / Rojo (<50)
- Tooltip que explica en qué se basa cada sub-score

### 2. Detección de las 10 causas de lentitud
Problemas que el agente detecta y el backend clasifica:

| ID | Problema | Señal que detecta el agente | Impacto en score |
|----|----------|----------------------------|-----------------|
| P01 | Thermal throttling | CPU freq actual < 80% de freq máxima del modelo | -20 Performance |
| P02 | Disco HDD con sectores pendientes | SMART C5 > 0 o C4 > 5 | -25 Storage |
| P03 | Memory leak activo | Proceso creció >150% RAM en >2h sesión | -15 Performance |
| P04 | Startup fantasmas | Entry sin binario existente | -5 Stability |
| P05 | SSD desgaste o lleno >90% | SMART TBW >85% life / disco >90% | -20 Storage |
| P06 | Drivers críticos desactualizados | Versión instalada vs latest del fabricante | -10 Stability |
| P07 | Cloud sync en loop (OneDrive/Drive) | Proceso sync >80% I/O por >30min | -10 Performance |
| P08 | Windows Update en background | wuauserv alto CPU+disco | -5 Performance |
| P09 | Antivirus escaneando silenciosamente | AV proceso >30% CPU por >15min | -5 Performance |
| P10 | Fragmentación severa / TRIM off | HDD >30% frag / SSD TRIM desactivado | -10 Storage |

### 3. Issue Cards con Fix en 1 click
Cada problema detectado genera una card con:
- Ícono de severidad (crítico/alto/medio/bajo)
- Título del problema en lenguaje simple
- Explicación breve (1-2 líneas)
- **Botón "Ver detalles"** → abre panel con explicación técnica completa + datos raw
- **Botón "Fix"** (cuando aplica) → envía comando al agente, muestra progreso

### 4. Startup Intelligence
Lista de todos los programas de inicio, categorizados:
- 🔒 **Esencial** — no tocar (sistema operativo, drivers)
- ✅ **Útil / bajo impacto** — bien tenerlo
- ⚠️ **Útil / alto impacto** — considera desactivar (+Xs al arranque)
- 👻 **Fantasma** — binario no existe, safe to remove
- ❓ **Desconocido** — revisar manualmente
- 🔴 **Sospechoso** — no reconocido + actividad de red

Fix disponible: desactivar con 1 click (reversible).

### 5. Monitoreo en tiempo real
Panel con métricas live (actualización cada 5 segundos):
- CPU: % uso, temperatura, frecuencia actual vs máxima
- RAM: % uso, top 5 procesos por consumo
- Disco: % ocupado, velocidad lectura/escritura en curso
- Red: upload/download en curso, top proceso por uso de red

### 6. Root Cause Explainer (Claude AI)
Cuando el Health Score < 70, el backend llama a Claude con:
- Los issues detectados + sus métricas
- El historial de los últimos 7 días
- El modelo exacto del hardware

Claude responde con una explicación en lenguaje natural que aparece como "Diagnóstico del Doctor SysDoc" arriba del issue list.

Ejemplo: *"Tu computador está funcionando al 60% de su capacidad normal. La causa principal es que el procesador se está auto-limitando porque está demasiado caliente (94°C, normal es 75°C). Esto pasa cuando hay polvo acumulado en los ventiladores. Además, Chrome está usando 3.2GB de memoria — el doble de lo normal — posiblemente por demasiadas pestañas abiertas."*

### 7. Registro de máquina
- El agente genera un `machine_id` único en la instalación
- Se registra en el backend con: OS, modelo CPU, RAM total, nombre del host
- El dashboard muestra la máquina con su último scan timestamp

---

## Features — Fase 2 (post-MVP)

- **Trending histórico:** Gráficas de 30/90 días de temperatura, boot time, RAM usage
- **Multi-machine dashboard:** Monitorear múltiples equipos desde una sola vista
- **Alertas proactivas:** "Tu disco llenará en ~3 semanas a este ritmo"
- **Driver updater:** Links directos a downloads de drivers más recientes
- **Report export:** PDF con diagnóstico completo para llevar al técnico
- **"Ask the Doctor":** Chat conversacional — "solo se pone lento con videollamadas"
- **Benchmark:** Comparar métricas vs otros equipos del mismo modelo
- **Mobile view:** Dashboard responsivo para ver desde teléfono

---

## Esquema de base de datos (Supabase PostgreSQL)

```sql
-- Máquinas registradas
machines (
  id          UUID PRIMARY KEY,
  machine_id  TEXT UNIQUE,           -- generado por el agente
  hostname    TEXT,
  os_name     TEXT,                  -- "Windows 11 Pro", "macOS 14.5", "Ubuntu 24.04"
  os_arch     TEXT,                  -- "x86_64", "arm64"
  cpu_model   TEXT,
  cpu_cores   INT,
  ram_total_gb FLOAT,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  last_seen   TIMESTAMPTZ
)

-- Scans (snapshots completos del sistema)
scans (
  id          UUID PRIMARY KEY,
  machine_id  UUID REFERENCES machines(id),
  scanned_at  TIMESTAMPTZ DEFAULT NOW(),
  health_score INT,                  -- 0-100
  score_performance INT,
  score_storage     INT,
  score_security    INT,
  score_stability   INT,
  raw_data    JSONB                  -- datos completos del agente
)

-- Issues detectados por scan
issues (
  id          UUID PRIMARY KEY,
  scan_id     UUID REFERENCES scans(id),
  machine_id  UUID REFERENCES machines(id),
  issue_code  TEXT,                  -- "P01", "P02", etc.
  severity    TEXT,                  -- "critical", "high", "medium", "low"
  title       TEXT,
  description TEXT,
  fix_available BOOLEAN DEFAULT FALSE,
  fix_command TEXT,                  -- comando a enviar al agente
  resolved_at TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT NOW()
)

-- Métricas de series de tiempo
metrics (
  id          UUID PRIMARY KEY,
  machine_id  UUID REFERENCES machines(id),
  recorded_at TIMESTAMPTZ DEFAULT NOW(),
  cpu_usage_pct      FLOAT,
  cpu_temp_c         FLOAT,
  cpu_freq_mhz       FLOAT,
  cpu_freq_max_mhz   FLOAT,
  ram_usage_pct      FLOAT,
  ram_available_gb   FLOAT,
  disk_read_mbps     FLOAT,
  disk_write_mbps    FLOAT,
  disk_usage_pct     FLOAT,
  net_upload_mbps    FLOAT,
  net_download_mbps  FLOAT
)

-- Historial de fixes aplicados
fix_history (
  id          UUID PRIMARY KEY,
  machine_id  UUID REFERENCES machines(id),
  issue_id    UUID REFERENCES issues(id),
  fix_code    TEXT,
  applied_at  TIMESTAMPTZ DEFAULT NOW(),
  success     BOOLEAN,
  output      TEXT
)
```

---

## API Endpoints (FastAPI)

```
POST   /api/v1/machines/register          → Registrar nueva máquina
POST   /api/v1/machines/{id}/scan         → Recibir scan del agente
GET    /api/v1/machines/{id}/dashboard    → Datos completos para el dashboard
GET    /api/v1/machines/{id}/issues       → Issues activos
GET    /api/v1/machines/{id}/metrics      → Serie de tiempo (últimas N horas)
POST   /api/v1/machines/{id}/fix          → Encolar fix para el agente
GET    /api/v1/machines/{id}/fix/{fix_id} → Estado del fix

POST   /api/v1/ai/explain                 → Claude root cause analysis
```

### Protocolo del agente (polling)
```
Cada 30s: POST /api/v1/machines/{id}/scan
  Body: { metrics, processes, startup_items, smart_data, drivers }

Cada 5s:  GET  /api/v1/machines/{id}/pending_commands
  Response: { commands: [{ id, type, params }] }

Después de ejecutar: POST /api/v1/machines/{id}/fix/{id}/result
```

---

## Estructura de archivos

```
sysdoc/
├── app/
│   ├── client/                    # Frontend React + Vite
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── ui/            # shadcn components
│   │   │   │   ├── HealthScore.tsx
│   │   │   │   ├── IssueCard.tsx
│   │   │   │   ├── MetricsPanel.tsx
│   │   │   │   ├── StartupList.tsx
│   │   │   │   └── RootCausePanel.tsx
│   │   │   ├── pages/
│   │   │   │   ├── Dashboard.tsx  # Vista principal
│   │   │   │   ├── Issues.tsx
│   │   │   │   ├── Metrics.tsx
│   │   │   │   └── Startup.tsx
│   │   │   ├── lib/
│   │   │   │   ├── api.ts         # API client (fetch wrapper)
│   │   │   │   └── utils.ts
│   │   │   ├── hooks/
│   │   │   │   └── useMachine.ts
│   │   │   └── main.tsx
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   ├── server/                    # Backend FastAPI
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── routers/
│   │   │   ├── machines.py
│   │   │   ├── scans.py
│   │   │   ├── fixes.py
│   │   │   └── ai.py
│   │   ├── models/
│   │   │   ├── machine.py         # Pydantic models
│   │   │   ├── scan.py
│   │   │   └── issue.py
│   │   ├── services/
│   │   │   ├── analyzer.py        # Issue detection logic
│   │   │   ├── scorer.py          # Health score calculation
│   │   │   └── ai_explainer.py    # Claude integration
│   │   ├── db/
│   │   │   └── supabase.py        # Supabase client
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   └── agent/                     # Agente local cross-platform
│       ├── main.py                # Entry point del daemon
│       ├── collectors/
│       │   ├── cpu.py             # CPU: freq, temp, throttling
│       │   ├── memory.py          # RAM: usage, leaks por proceso
│       │   ├── disk.py            # Disco: SMART, velocidad, fragmentación
│       │   ├── network.py         # Red: bandwidth por proceso
│       │   ├── processes.py       # Procesos: top consumers
│       │   ├── startup.py         # Programas de inicio
│       │   ├── drivers.py         # Drivers: versiones
│       │   └── security.py        # Seguridad: firewall, updates
│       ├── fixers/
│       │   ├── startup_fixer.py   # Desactivar startup programs
│       │   ├── disk_fixer.py      # TRIM, desfragmentación
│       │   └── process_fixer.py   # Matar memory-leak processes
│       ├── client.py              # HTTP client hacia backend
│       └── pyproject.toml
│
├── adws/                          # ADW system (no tocar)
├── .claude/                       # Claude Code config (no tocar)
├── scripts/                       # Utility scripts
├── CLAUDE.md                      # Context rápido del proyecto
├── INIT.md                        # Este documento
└── .env.sample
```

---

## Variables de entorno

```bash
# Backend
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...   # Solo backend
ANTHROPIC_API_KEY=sk-ant-...

# Frontend
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...

# Agente
SYSDOC_API_URL=http://localhost:8000   # o URL de producción
SYSDOC_MACHINE_ID=                     # Auto-generado en instalación
```

---

## Fases de implementación

### Fase 1 — Agente + Backend + Dashboard básico (MVP)
1. **Agente:** colectores de CPU, RAM, disco, procesos
2. **Backend:** endpoints de registro y scan, lógica de detección P01–P10, health score
3. **Frontend:** Dashboard con Health Score, lista de issues, métricas en tiempo real
4. **Claude integration:** Root cause explainer

### Fase 2 — Fixes + Startup Intelligence
5. **Agente:** fixers (startup, TRIM, process killer)
6. **Frontend:** Fix buttons, Startup Intelligence panel
7. **Backend:** command queue para el agente

### Fase 3 — Histórico + Multi-machine
8. **Backend:** jobs de análisis de tendencias
9. **Frontend:** gráficas históricas (Recharts)
10. **Frontend:** Multi-machine dashboard

### Fase 4 — Deploy + Pulido
11. Deploy frontend → Vercel
12. Deploy backend → Railway
13. Setup Supabase producción
14. Agente packaged con PyInstaller

---

## Comandos de desarrollo

```bash
# Instalar todo
cd app/client && bun install
cd app/server && uv sync
cd app/agent && uv sync

# Iniciar
./scripts/start.sh
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# Docs API: http://localhost:8000/docs

# Tests
cd app/server && uv run pytest
cd app/client && bun tsc --noEmit
cd app/agent && uv run pytest

# Ver logs del agente (modo debug)
cd app/agent && uv run python main.py --debug
```

---

## Para la nueva sesión de Claude Code

Al abrir este proyecto en Claude Code, ejecuta:

```
/prime
```

Luego puedes iniciar directo con:
```
/feature
```

Para crear el primer issue en GitHub y arrancar el SDLC completo con ADW.

O desarrollar interactivamente paso a paso leyendo este `INIT.md` como guía.

---

*Análisis competitivo basado en: CCleaner, CleanMyMac X, HWiNFO64, CrystalDiskInfo, Speccy, Stacer, iStatMenus, Process Monitor, WhySoSlow, Malwarebytes, Dell SupportAssist, HP Support Assistant — Mayo 2026.*

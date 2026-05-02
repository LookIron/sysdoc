from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, machines, scans, ai, dashboard, fixes

app = FastAPI(title="SysDoc API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(machines.router)
app.include_router(scans.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
app.include_router(fixes.router)

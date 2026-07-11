from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from api.agents import router as agents_router
from api.alerts import router as alerts_router
from api.cases import router as cases_router
from api.analytics import router as analytics_router
from api.simulator import router as simulator_router
from api.ws import manager
from scheduler.poller import poll_once

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(poll_once, "interval", seconds=30, id="poller", replace_existing=True)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="Multi-Provider Agent Liquidity Dashboard",
    description="bKash x SUST CSE Carnival 2026 — Hackathon API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router)
app.include_router(alerts_router)
app.include_router(cases_router)
app.include_router(analytics_router)
app.include_router(simulator_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()   # keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "liquidity-dashboard"}


@app.post("/api/seed")
async def seed_endpoint():
    from data.seed import seed
    await seed()
    return {"status": "seeded"}

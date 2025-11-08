from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from redis import Redis
import logging
from datetime import datetime
from config.settings import settings
from api.routes import data_router, migration_router, analytics_router
from api.routes.upload import router as upload_router
from api.routes.auth import router as auth_router
from api.routes.credentials import router as credentials_router
from api.routes.recommendations import router as recommendations_router
from api.routes.metrics import router as metrics_router
from streaming.websocket_manager import websocket_manager

app = FastAPI(title="CloudFlow Intelligence Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

from middleware.rate_limiter import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)

mongodb_client = None
redis_client = None

@app.on_event("startup")
async def startup_event():
    global mongodb_client, redis_client
    mongodb_client = MongoClient(settings.mongodb_url)
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    logging.info("Database connections established")

@app.on_event("shutdown")
async def shutdown_event():
    global mongodb_client, redis_client
    if mongodb_client:
        mongodb_client.close()
    if redis_client:
        redis_client.close()
    logging.info("Database connections closed")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "timestamp": datetime.utcnow().isoformat()}
    )

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mongodb": "connected" if mongodb_client else "disconnected",
        "redis": "connected" if redis_client else "disconnected"
    }

def get_redis():
    return redis_client

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_personal({"message": "pong"}, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

app.include_router(auth_router)
app.include_router(credentials_router)
app.include_router(data_router)
app.include_router(migration_router)
app.include_router(analytics_router)
app.include_router(upload_router)
app.include_router(recommendations_router)
app.include_router(metrics_router)

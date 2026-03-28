from fastapi import APIRouter
from app.api import auth, ws, alerts

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(ws.router, tags=["websocket"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])

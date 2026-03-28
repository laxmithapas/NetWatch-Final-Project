from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.api_router import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.models import user, alert
from app.core.simulator import run_simulation
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup Tasks
    print("NetWatch Backend starting up...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    # Start Simulation
    simulation_task = asyncio.create_task(run_simulation())
    
    yield
    
    # Teardown Tasks
    simulation_task.cancel()
    print("NetWatch Backend shutting down...")

app = FastAPI(
    title="NetWatch NIDS API",
    description="Real-Time Network Intrusion Detection System backend",
    version="1.0.0",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to NetWatch API"}

app.include_router(api_router, prefix=settings.API_V1_STR)

import os
# Serve ML Plots
plots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ml_pipeline", "plots")
if os.path.exists(plots_dir):
    app.mount("/plots", StaticFiles(directory=plots_dir), name="plots")

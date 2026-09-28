from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import dashboard
from api.routes import forecast
from api.routes import risk
from api.routes import ai

app = FastAPI(
    title="GridMind AI Energy Intelligence API",
    description="AI-powered energy forecasting, anomaly detection and grid decision intelligence platform.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    forecast.router,
    prefix="/forecast",
    tags=["Forecast"]
)

app.include_router(
    risk.router,
    prefix="/risk",
    tags=["Grid Risk"]
)

app.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI Analyst"]
)

# Website
app.mount(
    "/",
    StaticFiles(
        directory=r"D:\GridMind\frontend",
        html=True
    ),
    name="frontend"
)
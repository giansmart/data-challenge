from fastapi import FastAPI

from app.routers import analytics, ingestion

app = FastAPI(title="Data Challenge API")
app.include_router(ingestion.router)
app.include_router(analytics.router)

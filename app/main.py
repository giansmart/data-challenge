from fastapi import FastAPI

from app.routers import ingestion

app = FastAPI(title="Data Challenge API")
app.include_router(ingestion.router)

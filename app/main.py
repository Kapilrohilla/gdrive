from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.api.v1.endpoints import short_url
from app.config import settings
from app.core.database.database import lifespan

app = FastAPI(lifespan=lifespan, title="CloudDrive API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(short_url.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

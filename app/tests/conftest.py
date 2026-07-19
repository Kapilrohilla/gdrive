import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient

from app.api.v1.api import api_router
from app.config import settings


def create_test_app() -> FastAPI:
    test_app = FastAPI(title="CloudDrive API Test")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(api_router)

    @test_app.get("/")
    def read_root():
        return {"name": "CloudDrive API", "version": "0.1.0"}

    return test_app


@pytest.fixture
async def client():
    app = create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

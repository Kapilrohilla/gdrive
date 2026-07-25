from fastapi import APIRouter

from app.api.v1.endpoints import auth, files, folders, rbac, users, visitor

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(rbac.router)
api_router.include_router(users.router)
api_router.include_router(folders.router)
api_router.include_router(files.router)
api_router.include_router(visitor.router)

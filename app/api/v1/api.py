from fastapi import APIRouter

from app.api.v1.endpoints import auth, drive, files, folders, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(folders.router)
api_router.include_router(files.router)
api_router.include_router(drive.router)

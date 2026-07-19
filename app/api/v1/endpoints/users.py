from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.user import CreateUserDto
from app.services.user import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await user_service.get_user(db)
    return users


@router.post("/")
async def create_user(payload: CreateUserDto, db: AsyncSession = Depends(get_db)):
    data = await user_service.create_user(payload.full_name, db)
    return {"message": "User created", "data": data, "timestamp": datetime.now()}

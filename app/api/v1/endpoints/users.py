from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.users import CreateUserRequest, CreateUserResponse
from app.services.user import user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)


@router.get("/")
async def get_users(db: DbSession):
    users = await user_service.get_user(db)
    return users


@router.post("/", response_model=CreateUserResponse)
async def create_user(payload: CreateUserRequest, db: DbSession):
    data = await user_service.create_user(db=db, full_name=payload.full_name)
    return {"message": "User created", "data": data, "timestamp": datetime.now()}

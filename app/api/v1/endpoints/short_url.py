from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.api.deps import DbSession
from app.config import settings
from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.short_url import (
    ShortenUrlRequest,
    ShortenUrlResponse,
    ShortUrlItem,
    ShortUrlListResponse,
)
from app.services.short_urls import ShortUrlsService
from app.services.utils.encoding import EncodingService

prefix = "/s"
router = APIRouter(
    prefix=prefix,
    tags=["Short URL"],
)

encoding_service = EncodingService()
short_url_service = ShortUrlsService(encoding_service)


@router.post(
    "/shorten",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=ShortenUrlResponse,
)
async def shorten(payload: ShortenUrlRequest, request: Request, db: DbSession):
    user_id = UUID(str(request.state.user_id))
    short_code = await short_url_service.shorten(db, payload.long_url, user_id)
    return {"short_url": f"{settings.host_url}{prefix}/{short_code}"}


@router.get(
    "/",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=ShortUrlListResponse,
)
async def get_short_urls(request: Request, db: DbSession):
    user_id = UUID(str(request.state.user_id))
    records = await short_url_service.get_short_urls(db, user_id)
    return {
        "short_urls": [
            ShortUrlItem(
                id=record.id,
                original_url=record.original_url,
                short_code=record.short_code,
                short_url=f"{settings.host_url}{prefix}/{record.short_code}",
                created_at=record.created_at,
            )
            for record in records
            if record.short_code is not None
        ]
    }


@router.get("/{short_code}")
async def redirect_short_url(short_code: str, db: DbSession):
    original_url = await short_url_service.resolve(db, short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=original_url, status_code=307)


__all__ = ["router"]

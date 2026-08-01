from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ShortenUrlRequest(BaseModel):
    long_url: str = Field(min_length=1)


class ShortenUrlResponse(BaseModel):
    short_url: str


class ShortUrlItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime


class ShortUrlListResponse(BaseModel):
    short_urls: list[ShortUrlItem]

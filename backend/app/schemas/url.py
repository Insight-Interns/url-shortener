from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ShortenURLRequest(BaseModel):
    long_url: str = Field(..., description="The original long destination URL")
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=30, description="Optional custom short code")
    expires_at: Optional[datetime] = Field(None, description="Optional ISO timestamp for link expiration")


class ShortenURLResponse(BaseModel):
    short_url: str
    short_code: str
    long_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None


class BulkShortenRequest(BaseModel):
    urls: List[ShortenURLRequest] = Field(..., max_length=50, description="List of URLs to shorten in bulk (max 50)")


class URLItemResponse(BaseModel):
    id: str
    short_code: str
    long_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    created_by: Optional[str]
    click_count: int = 0


import re
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, field_validator

ALIAS_RE = re.compile(r"^[A-Za-z0-9_-]{3,20}$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class ShortenRequest(BaseModel):
    long_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

    @field_validator("long_url")
    @classmethod
    def validate_long_url(cls, v: str) -> str:
        v = v.strip()
        if not URL_RE.match(v):
            raise ValueError("long_url must start with http:// or https://")
        if len(v) > 2048:
            raise ValueError("long_url is too long")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if not ALIAS_RE.match(v):
            raise ValueError(
                "custom_alias must be 3-20 characters: letters, digits, hyphen, underscore"
            )
        return v

    @field_validator("expires_at", mode="before")
    @classmethod
    def normalize_expires_at(cls, v):
        # A bare date (e.g. from an <input type="date">, "2026-08-01") is
        # normalized to end-of-day so the link stays valid through the whole
        # selected day; full ISO datetimes pass through untouched.
        if v is None or v == "":
            return None
        if isinstance(v, str) and len(v) == 10:
            d = date.fromisoformat(v)
            return datetime.combine(d, time(23, 59, 59))
        return v


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str


class BreakdownItem(BaseModel):
    label: str
    count: int


class ClicksOverTimePoint(BaseModel):
    date: date
    count: int


class AnalyticsResponse(BaseModel):
    short_code: str
    long_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    total_clicks: int
    device_breakdown: list[BreakdownItem]
    location_breakdown: list[BreakdownItem]
    clicks_over_time: list[ClicksOverTimePoint]

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app import crud
from app.database import get_conn
from app.schemas import AnalyticsResponse, BreakdownItem, ClicksOverTimePoint

router = APIRouter()


@router.get("/api/analytics/{short_code}", response_model=AnalyticsResponse)
def get_analytics(short_code: str, conn: Connection = Depends(get_conn)):
    url = crud.get_url_by_short_code(conn, short_code)
    if url is None:
        raise HTTPException(status_code=404, detail="short link not found")

    total_clicks = crud.get_total_clicks(conn, url["id"])
    device_breakdown = [BreakdownItem(**row) for row in crud.get_device_breakdown(conn, url["id"])]
    location_breakdown = [
        BreakdownItem(**row) for row in crud.get_location_breakdown(conn, url["id"])
    ]
    clicks_over_time = [
        ClicksOverTimePoint(**row) for row in crud.get_clicks_over_time(conn, url["id"])
    ]

    return AnalyticsResponse(
        short_code=url["short_code"],
        long_url=url["long_url"],
        created_at=url["created_at"],
        expires_at=url["expires_at"],
        total_clicks=total_clicks,
        device_breakdown=device_breakdown,
        location_breakdown=location_breakdown,
        clicks_over_time=clicks_over_time,
    )

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from psycopg import Connection

from app import crud
from app.database import get_conn
from app.geoip import geolocate, get_client_ip
from app.user_agent import get_device_type

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{short_code}")
def redirect_short_code(short_code: str, request: Request, conn: Connection = Depends(get_conn)):
    url = crud.get_url_by_short_code(conn, short_code)
    if url is None:
        return JSONResponse(status_code=404, content={"detail": "short link not found"})

    expires_at = url["expires_at"]
    if expires_at is not None:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return JSONResponse(status_code=410, content={"detail": "this link has expired"})

    try:
        ip = get_client_ip(request)
        device_type = get_device_type(request.headers.get("user-agent", ""))
        location = geolocate(ip)
        referrer = request.headers.get("referer")
        crud.log_click(conn, url["id"], device_type, location, referrer)
    except Exception:
        # Click logging (including the external geolocation call) must never
        # block or break the actual redirect.
        logger.exception("failed to log click for short_code=%s", short_code)

    return RedirectResponse(url=url["long_url"], status_code=302)

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app import crud
from app.config import settings
from app.database import get_conn
from app.schemas import ShortenRequest, ShortenResponse

router = APIRouter()


@router.post("/api/shorten", response_model=ShortenResponse, status_code=201)
def shorten_url(payload: ShortenRequest, conn: Connection = Depends(get_conn)):
    if payload.custom_alias:
        if crud.alias_exists(conn, payload.custom_alias):
            raise HTTPException(status_code=409, detail="custom_alias is already taken")
        try:
            code = crud.insert_custom_url(
                conn, payload.custom_alias, payload.long_url, payload.expires_at
            )
        except crud.AliasTakenError:
            raise HTTPException(status_code=409, detail="custom_alias is already taken")
    else:
        code = crud.insert_auto_url(conn, payload.long_url, payload.expires_at)

    return ShortenResponse(short_code=code, short_url=f"{settings.base_url.rstrip('/')}/{code}")

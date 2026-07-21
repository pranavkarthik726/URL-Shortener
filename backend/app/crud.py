from datetime import datetime
from typing import Optional

from psycopg import Connection
from psycopg.errors import UniqueViolation

from app import base62


class AliasTakenError(Exception):
    pass


def get_url_by_short_code(conn: Connection, short_code: str) -> Optional[dict]:
    return conn.execute(
        "SELECT id, short_code, long_url, is_custom_alias, created_at, expires_at "
        "FROM urls WHERE short_code = %s",
        (short_code,),
    ).fetchone()


def alias_exists(conn: Connection, alias: str) -> bool:
    row = conn.execute("SELECT 1 FROM urls WHERE short_code = %s", (alias,)).fetchone()
    return row is not None


def insert_custom_url(
    conn: Connection, alias: str, long_url: str, expires_at: Optional[datetime]
) -> str:
    try:
        with conn.transaction():
            conn.execute(
                "INSERT INTO urls (short_code, long_url, is_custom_alias, expires_at) "
                "VALUES (%s, %s, TRUE, %s)",
                (alias, long_url, expires_at),
            )
    except UniqueViolation as exc:
        raise AliasTakenError(alias) from exc
    return alias


def insert_auto_url(conn: Connection, long_url: str, expires_at: Optional[datetime]) -> str:
    row = conn.execute(
        "INSERT INTO urls (short_code, long_url, is_custom_alias, expires_at) "
        "VALUES (NULL, %s, FALSE, %s) RETURNING id",
        (long_url, expires_at),
    ).fetchone()
    url_id = row["id"]
    code = base62.encode(url_id)
    try:
        with conn.transaction():  # savepoint, so a collision doesn't abort the outer insert
            conn.execute("UPDATE urls SET short_code = %s WHERE id = %s", (code, url_id))
    except UniqueViolation:
        # A previously claimed custom alias happens to equal this id's Base62
        # code. id is already globally unique, so appending it deterministically
        # resolves the clash without a retry loop.
        code = f"{code}-{url_id}"
        conn.execute("UPDATE urls SET short_code = %s WHERE id = %s", (code, url_id))
    return code


def log_click(
    conn: Connection,
    url_id: int,
    device_type: str,
    location: str,
    referrer: Optional[str],
) -> None:
    conn.execute(
        "INSERT INTO clicks (url_id, device_type, location, referrer) VALUES (%s, %s, %s, %s)",
        (url_id, device_type, location, referrer),
    )


def get_total_clicks(conn: Connection, url_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS count FROM clicks WHERE url_id = %s", (url_id,)
    ).fetchone()
    return row["count"]


def get_device_breakdown(conn: Connection, url_id: int) -> list[dict]:
    return conn.execute(
        "SELECT COALESCE(device_type, 'unknown') AS label, COUNT(*) AS count "
        "FROM clicks WHERE url_id = %s GROUP BY label ORDER BY count DESC",
        (url_id,),
    ).fetchall()


def get_location_breakdown(conn: Connection, url_id: int, limit: int = 20) -> list[dict]:
    return conn.execute(
        "SELECT COALESCE(location, 'Unknown') AS label, COUNT(*) AS count "
        "FROM clicks WHERE url_id = %s GROUP BY label ORDER BY count DESC LIMIT %s",
        (url_id, limit),
    ).fetchall()


def get_clicks_over_time(conn: Connection, url_id: int) -> list[dict]:
    return conn.execute(
        "SELECT date_trunc('day', clicked_at)::date AS date, COUNT(*) AS count "
        "FROM clicks WHERE url_id = %s GROUP BY date ORDER BY date",
        (url_id,),
    ).fetchall()

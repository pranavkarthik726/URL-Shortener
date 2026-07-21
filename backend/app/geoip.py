import ipaddress

import httpx
from fastapi import Request


def get_client_ip(request: Request) -> str:
    # Railway sits behind a reverse proxy; the real client IP is the first
    # hop in X-Forwarded-For, not request.client.host.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def geolocate(ip: str) -> str:
    try:
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_loopback:
            # Localhost/private IP during dev — never call the external API,
            # both to avoid burning ip-api.com's free-tier rate limit and
            # because it can't geolocate a private address anyway.
            return "Local/Unknown"
    except ValueError:
        return "Unknown"

    try:
        resp = httpx.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,regionName,city"},
            timeout=2.0,
        )
        data = resp.json()
        if data.get("status") == "success":
            return f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
    except httpx.HTTPError:
        pass
    return "Unknown"

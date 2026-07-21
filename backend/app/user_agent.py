from user_agents import parse


def get_device_type(ua_string: str) -> str:
    ua = parse(ua_string or "")
    if ua.is_bot:
        return "bot"
    if ua.is_mobile:
        return "mobile"
    if ua.is_tablet:
        return "tablet"
    if ua.is_pc:
        return "desktop"
    return "other"

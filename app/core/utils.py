from datetime import timedelta
import re
import zoneinfo

from django.utils import timezone


def get_time_threshold(
    minutes: int, timezone: str = "Asia/Taipei"
) -> timezone.datetime:
    current_time = timezone.localtime(
        timezone.now(), timezone=zoneinfo.ZoneInfo(key=timezone)
    )
    return current_time - timedelta(minutes=minutes)


def is_valid_email(value: str) -> bool:
    return re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", value)


def is_valid_password(value: str, min_length: int) -> bool:
    allowed_symbols = r"!@#$%^&*()-_=+[]{}|;:,.<>/?~"
    password_pattern = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*["
        + re.escape(allowed_symbols)
        + r"])[a-zA-Z\d"
        + re.escape(allowed_symbols)
        + r"]{"
        + str(min_length)
        + r",}$"
    )

    return re.match(password_pattern, value)


def is_slug_invalid(value: str) -> bool:
    return (
        not value
        or re.search(r"\W", value.replace("-", ""))
        or any(str in value for str in ["\\"])
    )

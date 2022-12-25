import re


def is_valid_email(value: str) -> bool:
    return re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", value)

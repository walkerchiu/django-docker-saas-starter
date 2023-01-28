from functools import wraps
import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def google_captcha3(action):
    def decorator(func):
        @wraps(func)
        def wrapper(info, *args, **input):
            if settings.CAPTCHA["google_recaptcha3"]["enabled"]:
                data = {
                    "secret": settings.CAPTCHA["google_recaptcha3"]["key_private"],
                    "response": input["captcha"],
                }
                try:
                    r = requests.post(
                        settings.CAPTCHA["google_recaptcha3"]["endpoint"],
                        data=data,
                        timeout=settings.CAPTCHA["google_recaptcha3"]["timeout"],
                    )
                    res = r.json()

                    threshold: float = settings.CAPTCHA["google_recaptcha3"][
                        "threshold"
                    ]["default"]
                    if action in settings.CAPTCHA["google_recaptcha3"]["threshold"]:
                        threshold: float = settings.CAPTCHA["google_recaptcha3"][
                            "threshold"
                        ][action]

                    if not all(
                        (
                            res["success"],
                            res["score"] > threshold,
                            res["action"] == action,
                        )
                    ):
                        raise ValidationError(_("Captcha Error!"))
                except:
                    raise ValidationError(_("Captcha Error!"))

            result = func(info, *args, **input)

            return result

        return wrapper

    return decorator


def strip_input(func):
    @wraps(func)
    def wrapper(info, *args, **input):
        for key, item in input.items():
            if isinstance(item, str):
                input[key] = item.strip()
            elif isinstance(item, list):
                new = []
                for value in item:
                    if isinstance(value, str):
                        new.append(value.strip())
                    else:
                        new.append(value)
                input[key] = new
            else:
                input[key] = item

        result = func(info, *args, **input)

        return result

    return wrapper

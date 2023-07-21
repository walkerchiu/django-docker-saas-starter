from functools import wraps
import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection
from django.utils.translation import gettext as _

from tenant.helpers.contract_helper import ContractHelper


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


def within_validity_period(func):
    @wraps(func)
    def wrapper(self, *args, **input):
        info = args[1]
        endpoint = info.context.headers.get("X-Endpoint")

        if endpoint != "hq":
            contract_helper = ContractHelper(schema_name=connection.schema_name)
            if not contract_helper.check_if_it_is_within_the_validity_period():
                raise ValidationError("Not within the validity period!")

        result = func(self, *args, **input)

        return result

    return wrapper


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

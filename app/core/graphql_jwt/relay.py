from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.dispatch import receiver
from django.utils import timezone

from django_tenants.utils import schema_context
from graphene.utils.thenables import maybe_thenable
from graphql_jwt.refresh_token.signals import (
    refresh_token_rotated,
    refresh_token_revoked,
)
from graphql_jwt.signals import token_issued, token_refreshed
import graphene

from core.decorators import google_captcha3
from core.graphql_jwt import mixins
from core.graphql_jwt.decorators import token_auth
from core.graphql_jwt.refresh_token.relay import DeleteRefreshTokenCookie, Revoke
from tenant.models import Tenant

__all__ = [
    "JSONWebTokenMutation",
    "ObtainJSONWebToken",
    "Verify",
    "Refresh",
    "Revoke",
    "DeleteRefreshTokenCookie",
]


class JSONWebTokenMutation(mixins.ObtainJSONWebTokenMixin, graphene.ClientIDMutation):
    class Meta:
        abstract = True

    @classmethod
    def Field(cls, *args, **kwargs):
        cls._meta.arguments["input"]._meta.fields.update(
            {
                get_user_model().USERNAME_FIELD: graphene.InputField(
                    graphene.String,
                    required=True,
                ),
                "password": graphene.InputField(graphene.String, required=True),
                "captcha": graphene.InputField(
                    graphene.String,
                    required=settings.CAPTCHA["google_recaptcha3"]["enabled"],
                ),
            },
        )
        return super().Field(*args, **kwargs)

    @classmethod
    def mutate(cls, root, info, input):
        def on_resolve(payload):
            try:
                payload.client_mutation_id = input.get("client_mutation_id")
            except Exception:
                raise Exception(
                    f"Cannot set client_mutation_id in the payload object {repr(payload)}"
                )
            return payload

        schema_name = connection.schema_name

        if (
            info.context.headers.get("X-Tenant")
            == "account" + "." + settings.DOMAIN_WEBSITE
        ):
            with schema_context(settings.PUBLIC_SCHEMA_NAME):
                tenant = (
                    Tenant.objects.filter(email=input.get("email"))
                    .order_by("created_at")
                    .first()
                )
                if tenant:
                    schema_name = tenant.schema_name
                else:
                    raise Exception("Please enter valid credentials")

        with schema_context(schema_name):
            result = cls.mutate_and_get_payload(root, info, **input)
            return maybe_thenable(result, on_resolve)

    @classmethod
    @token_auth
    def mutate_and_get_payload(cls, root, info, **kwargs):
        return cls.resolve(root, info, **kwargs)


class ObtainJSONWebToken(mixins.ResolveMixin, JSONWebTokenMutation):
    """Obtain JSON Web Token mutation"""


class Verify(mixins.VerifyMixin, graphene.ClientIDMutation):
    class Input:
        token = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, *args, **kwargs):
        return cls.verify(*args, **kwargs)


class Refresh(mixins.RefreshMixin, graphene.ClientIDMutation):
    class Input(mixins.RefreshMixin.Fields):
        captcha = graphene.String(
            required=settings.CAPTCHA["google_recaptcha3"]["enabled"]
        )

    @classmethod
    @google_captcha3("auth")
    def mutate_and_get_payload(cls, *args, **kwargs):
        return cls.refresh(*args, **kwargs)


class DeleteJSONWebTokenCookie(
    mixins.DeleteJSONWebTokenCookieMixin,
    graphene.ClientIDMutation,
):
    @classmethod
    def mutate_and_get_payload(cls, *args, **kwargs):
        return cls.delete_cookie(*args, **kwargs)


# https://django-graphql-jwt.domake.io/signals.html#token-issued
@receiver(token_issued)
def token_issued(sender, request, user, **kwargs):
    user.last_login = timezone.now()
    user.save()


# https://django-graphql-jwt.domake.io/signals.html#token-refreshed
@receiver(token_refreshed)
def token_refreshed(sender, request, user, **kwargs):
    pass


# https://django-graphql-jwt.domake.io/signals.html#refresh-token-rotated
@receiver(refresh_token_rotated)
def refresh_token_rotated(
    sender, request, refresh_token: str, refresh_token_issued: str = None, **kwargs
):
    pass


# https://django-graphql-jwt.domake.io/signals.html#refresh-token-revoked
@receiver(refresh_token_revoked)
def refresh_token_revoked(sender, request, refresh_token: str, **kwargs):
    pass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection

from django_tenants.utils import schema_context
from graphene.utils.thenables import maybe_thenable
from graphql_jwt.refresh_token.mutations import DeleteRefreshTokenCookie, Revoke
import graphene

from core.graphql_jwt import mixins
from core.graphql_jwt.decorators import token_auth
from tenant.models import Tenant

__all__ = [
    "JSONWebTokenMutation",
    "ObtainJSONWebToken",
    "Verify",
    "Refresh",
    "Revoke",
    "DeleteRefreshTokenCookie",
]


class JSONWebTokenMutation(mixins.ObtainJSONWebTokenMixin, graphene.Mutation):
    class Meta:
        abstract = True

    @classmethod
    def Field(cls, *args, **kwargs):
        cls._meta.arguments.update(
            {
                get_user_model().USERNAME_FIELD: graphene.String(required=True),
                "password": graphene.String(required=True),
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


class Verify(mixins.VerifyMixin, graphene.Mutation):
    class Arguments:
        token = graphene.String()

    @classmethod
    def mutate(cls, *args, **kwargs):
        return cls.verify(*args, **kwargs)


class Refresh(mixins.RefreshMixin, graphene.Mutation):
    class Arguments(mixins.RefreshMixin.Fields):
        """Refresh Arguments"""

    @classmethod
    def mutate(cls, *arg, **kwargs):
        return cls.refresh(*arg, **kwargs)


class DeleteJSONWebTokenCookie(mixins.DeleteJSONWebTokenCookieMixin, graphene.Mutation):
    @classmethod
    def mutate(cls, *args, **kwargs):
        return cls.delete_cookie(*args, **kwargs)

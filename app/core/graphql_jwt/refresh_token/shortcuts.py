from django.utils.functional import lazy
from django.utils.translation import gettext as _

from django_tenants.utils import schema_context
from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.settings import jwt_settings
from graphql_jwt.refresh_token.utils import get_refresh_token_model


def get_refresh_token(token, context=None):
    RefreshToken = get_refresh_token_model()

    try:
        return jwt_settings.JWT_GET_REFRESH_TOKEN_HANDLER(
            refresh_token_model=RefreshToken,
            token=token,
            context=context,
        )

    except RefreshToken.DoesNotExist:
        raise JSONWebTokenError(_("Invalid refresh token"))


def create_refresh_token(user, schema_name, refresh_token=None):
    with schema_context(schema_name):
        if refresh_token is not None and jwt_settings.JWT_REUSE_REFRESH_TOKENS:
            refresh_token.reuse()
            return refresh_token
        return get_refresh_token_model().objects.create(user=user)


refresh_token_lazy = lazy(
    lambda user, schema_name, refresh_token=None: create_refresh_token(
        user,
        schema_name,
        refresh_token,
    ).get_token(),
    str,
    str,
)

"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from app.schemas.schema_auth import schema as schema_auth
from app.schemas.schema_dashboard import schema as schema_dashboard
from app.schemas.schema_hq import schema as schema_hq
from app.schemas.schema_website import schema as schema_website
from app.views_api import version
from core.views import ErrorGraphQLView


# GraphQL
urlpatterns = [
    path("api/version", version, name="version"),
    path(
        "auth/graphql",
        ErrorGraphQLView.as_view(
            graphiql=settings.PLAYGROUND,
            schema=schema_auth,
        ),
    ),
    path(
        "dashboard/graphql",
        ErrorGraphQLView.as_view(
            graphiql=settings.PLAYGROUND,
            schema=schema_dashboard,
        ),
    ),
    path(
        "hq/graphql",
        ErrorGraphQLView.as_view(
            graphiql=settings.PLAYGROUND,
            schema=schema_hq,
        ),
    ),
    path(
        "website/graphql",
        ErrorGraphQLView.as_view(
            graphiql=settings.PLAYGROUND,
            schema=schema_website,
        ),
    ),
]

if settings.APP_ENV == "local":
    urlpatterns = (
        urlpatterns
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )

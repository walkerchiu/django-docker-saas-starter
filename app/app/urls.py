"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from core.backend import DepthAnalysisBackend
from core.views import ErrorGraphQLView


# GraphQL
urlpatterns = [
    path(
        "auth/graphql",
        ErrorGraphQLView.as_view(
            graphiql=True, schema=schema_auth, backend=DepthAnalysisBackend()
        ),
    ),
    path(
        "dashboard/graphql",
        ErrorGraphQLView.as_view(
            graphiql=True, schema=schema_dashboard, backend=DepthAnalysisBackend()
        ),
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

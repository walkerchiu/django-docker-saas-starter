import json

from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from django_tenants.utils import schema_context
from graphql import validate, parse
from graphene.validation import depth_limit_validator
from ipware import get_client_ip

from app.schemas.schema_auth import schema
from tenant.models import Domain


class DepthCheckMiddleware(MiddlewareMixin):
    def __call__(self, request: HttpRequest):
        if not settings.PLAYGROUND:
            body = json.loads(request.body.decode())
            query = body["query"]

            validation_errors = validate(
                schema=schema.graphql_schema,
                document_ast=parse(query),
                rules=(depth_limit_validator(max_depth=settings.GRAPHENE_MAX_DEPTH),),
            )
            if validation_errors:
                raise Exception("Query is too nested")

        response = self.get_response(request)

        return response


class DomainCorsMiddleware(MiddlewareMixin):
    def __call__(self, request: HttpRequest):
        for url in settings.CORS_ALLOWED_ORIGINS:
            https_url = url.replace("http://", "https://")
            if https_url not in settings.CORS_ALLOWED_ORIGINS:
                settings.CORS_ALLOWED_ORIGINS.append(https_url)
            if https_url not in settings.CORS_ORIGIN_WHITELIST:
                settings.CORS_ORIGIN_WHITELIST.append(https_url)

        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            domains = Domain.objects.values_list("domain", flat=True)
            for domain in domains:
                settings.CORS_ALLOWED_ORIGINS.append("https://" + domain)
                settings.CORS_ORIGIN_WHITELIST.append("https://" + domain)

        response = self.get_response(request)

        return response


class HealthCheckMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_allowed = []

    def __call__(self, request: HttpRequest):
        client_ip, is_routable = get_client_ip(request)
        if is_routable and client_ip in self.ip_allowed:
            settings.DEBUG = True

        if request.method == "GET" and (
            request.path == "/" or request.path == "/healthz"
        ):
            return HttpResponse("200")
        elif not settings.PLAYGROUND:
            if request.path.startswith("/auth/") and request.headers.get(
                "Authorization"
            ):
                raise Exception("This operation is not allowed!")
            elif request.path.startswith("/dashboard/") and not request.headers.get(
                "Authorization"
            ):
                raise Exception("This operation is not allowed!")

        response = self.get_response(request)

        return response

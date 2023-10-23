import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from django_tenants.utils import schema_context
from graphql import validate, parse
from graphene.validation import depth_limit_validator
from ipware import get_client_ip

from app.schemas.schema_auth import schema
from core.helpers.ip_helper import get_location_by_ip
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
                raise ValidationError("Query is too nested")

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
            if https_url not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append(https_url)

        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            domains = Domain.objects.values_list("domain", flat=True)
            for domain in domains:
                settings.CORS_ALLOWED_ORIGINS.append("https://" + domain)
                settings.CORS_ORIGIN_WHITELIST.append("https://" + domain)
                settings.CSRF_TRUSTED_ORIGINS.append("https://" + domain)

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
        else:
            if settings.PLAYGROUND and settings.APP_ENV not in ("local", "playground"):
                return HttpResponse("Unauthorized", status=401)
            settings.DEBUG = False

        if request.method == "GET" and (
            request.path == "/" or request.path == "/healthz"
        ):
            return HttpResponse("200")
        elif not settings.PLAYGROUND:
            if request.path.startswith("/auth/") and request.headers.get(
                "Authorization"
            ):
                raise ValidationError("This operation is not allowed!")
            elif request.path.startswith("/dashboard/") and not request.headers.get(
                "Authorization"
            ):
                raise ValidationError("This operation is not allowed!")

        response = self.get_response(request)

        return response


class HeaderHandlerMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.user_agent = request.headers.get("X-User-Agent", None)
        request.user_ip = request.headers.get("X-User-Ip", None)
        request.user_location = request.headers.get("X-User-Location", None)

        if request.user_ip and request.user_location is None:
            request.user_location = get_location_by_ip(request.user_ip)

        if not settings.PLAYGROUND:
            pass
            # if request.user_agent is None:
            #     raise ValidationError("Bad Request!")
            # elif request.user_ip is None:
            #     raise ValidationError("Bad Request!")
            # elif request.user_location is None:
            #     raise ValidationError("Bad Request!")

        response = self.get_response(request)

        return response

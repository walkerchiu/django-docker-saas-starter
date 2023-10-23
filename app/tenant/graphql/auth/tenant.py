from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from django_tenants.utils import schema_context
from graphql_jwt.settings import jwt_settings
from graphql_jwt.shortcuts import get_token
from graphene import ResolveInfo
from safedelete.models import HARD_DELETE
import graphene
import validators

from core.decorators import google_captcha3, strip_input
from core.utils import is_valid_email, is_valid_password
from organization.services.organization_service import OrganizationService
from tenant.graphql.auth.types.tenant import RegisterTenantResponseType, TenantNode
from tenant.models import Domain, Tenant
from tenant.services.tenant_service import TenantService


class RegisterTenant(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        organizationName = graphene.String(required=True)
        subdomain = graphene.String(required=True)
        captcha = graphene.String(
            required=settings.CAPTCHA["google_recaptcha3"]["enabled"]
        )

    success = graphene.Boolean()
    tenant = graphene.Field(RegisterTenantResponseType)

    @classmethod
    @strip_input
    @google_captcha3("auth")
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        subdomain_endpoint = info.context.headers.get("x-tenant").split(".")[0]
        if subdomain_endpoint != "account":
            raise ValidationError("This operation is not allowed!")

        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            email = input["email"]
            password = input["password"]
            organization_name = input["organizationName"]
            subdomain = input["subdomain"]

            if not is_valid_email(email):
                raise ValidationError("The email is invalid!")
            elif not is_valid_password(value=password, min_length=8):
                raise ValidationError("The password is invalid!")

            subdomain: str = subdomain.lower()
            domain: str = subdomain + "." + settings.DOMAIN_WEBSITE

            if not validators.domain(domain):
                raise ValidationError("The domain is invalid!")
            elif Tenant.objects.filter(email=email).exists():
                raise ValidationError("The email is already in use!")
            elif Domain.objects.filter(domain=domain).exists():
                raise ValidationError("The domain is already in use!")
            else:
                tenant_response = {"domain": None, "token": None, "payload": None}

                tenant_service = TenantService()
                result, tenant = tenant_service.create_tenant(
                    subdomain=subdomain,
                    email=email,
                )
                if result:
                    organization_service = OrganizationService()
                    result, organization, user = organization_service.initiate_schema(
                        schema_name=tenant.schema_name,
                        organization_name=organization_name,
                        email=email,
                        password=password,
                    )
                    if result:
                        with schema_context(organization.schema_name):
                            info.context.schema_name = organization.schema_name

                            tenant_response["domain"] = domain
                            tenant_response["token"] = get_token(user)
                            tenant_response[
                                "payload"
                            ] = jwt_settings.JWT_PAYLOAD_HANDLER(user, info.context)
                    else:
                        tenant.delete(force_policy=HARD_DELETE)

        return RegisterTenant(success=result, tenant=tenant_response)


class TenantMutation(graphene.ObjectType):
    tenant_register = RegisterTenant.Field()


class TenantQuery(graphene.ObjectType):
    tenant = graphene.relay.Node.Field(TenantNode)

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from django_tenants.utils import schema_context
from graphene import ResolveInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
import graphene
import validators

from core.decorators import strip_input
from core.types import TaskStatusType
from tenant.graphql.dashboard.types.domain import DomainNode
from tenant.models import Domain, Tenant
from tenant.variables.protected_subdomain import PROTECTED_SUBDOMAIN


class CreateDomain(graphene.relay.ClientIDMutation):
    class Input:
        tenantId = graphene.ID(required=True)
        domain = graphene.String(required=True)
        isPrimary = graphene.Boolean(required=True)

    success = graphene.Boolean()
    domain = graphene.Field(DomainNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            tenantId = input["tenantId"]
            value = input["domain"]
            isPrimary = input["isPrimary"]

            if not validators.domain(value):
                raise Exception("The domain is invalid!")
            elif value in PROTECTED_SUBDOMAIN:
                raise ValidationError("The domain is being protected!")
            elif Domain.objects.filter(domain=value).exists():
                raise ValidationError("The domain is already in use!")

            try:
                _, tenant_id = from_global_id(tenantId)

                tenant = Tenant.objects.get(id=tenant_id)
            except:
                raise Exception("Can not find this tenant!")

            domain = Domain(
                tenant=tenant, domain=value, is_primary=isPrimary, is_builtin=False
            )
            domain.save()

            if isPrimary:
                Domain.objects.filter(tenant=tenant, is_primary=True).update(
                    is_primary=False
                )

        return CreateDomain(success=True, domain=domain)


class DeleteDomainBatch(graphene.relay.ClientIDMutation):
    class Input:
        tenantId = graphene.ID(required=True)
        ids = graphene.List(graphene.ID, required=True)

    success = graphene.Boolean()
    warnings = graphene.Field(TaskStatusType)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            tenantId = input["tenantId"]
            ids = input["ids"] if "ids" in input else []

            try:
                _, tenant_id = from_global_id(tenantId)

                tenant = Tenant.objects.get(id=tenant_id)
            except:
                raise Exception("Can not find this tenant!")

            warnings = {
                "done": [],
                "error": [],
                "in_protected": [],
                "in_use": [],
                "not_found": [],
                "wait_to_do": [],
            }

            for id in ids:
                try:
                    _, domain_id = from_global_id(id)
                except:
                    warnings["error"].append(id)

                domain = (
                    Domain.objects.filter(tenant=tenant, is_builtin=False)
                    .only("id")
                    .get(pk=domain_id)
                )
                try:
                    if domain.is_primary:
                        warnings["in_protected"].append(id)
                    else:
                        domain.delete()

                        warnings["done"].append(id)
                except Domain.DoesNotExist:
                    warnings["not_found"].append(id)

        return DeleteDomainBatch(success=True, warnings=warnings)


class UpdateDomain(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        tenantId = graphene.ID(required=True)
        domain = graphene.String(required=True)
        isPrimary = graphene.Boolean(required=True)

    success = graphene.Boolean()
    domain = graphene.Field(DomainNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            id = input["id"]
            tenantId = input["tenantId"]
            value = input["domain"]
            isPrimary = input["isPrimary"]

            if not validators.domain(value):
                raise Exception("The domain is invalid!")
            elif value in PROTECTED_SUBDOMAIN:
                raise ValidationError("The domain is being protected!")

            try:
                _, tenant_id = from_global_id(tenantId)

                tenant = Tenant.objects.get(id=tenant_id)
            except:
                raise Exception("Can not find this tenant!")

            try:
                _, domain_id = from_global_id(id)

                domain = Domain.objects.get(
                    pk=domain_id, tenant=tenant, is_builtin=False
                )
            except:
                raise Exception("Can not find this domain!")

            if Domain.objects.filter(domain=value).exclude(pk=domain_id).exists():
                raise ValidationError("The domain is already in use!")

            domain.domain = value
            domain.is_primary = isPrimary
            domain.save()

            if isPrimary:
                Domain.objects.filter(tenant=tenant, is_primary=True).update(
                    is_primary=False
                )

        return UpdateDomain(success=True, domain=domain)


class DomainMutation(graphene.ObjectType):
    domain_create = CreateDomain.Field()
    domain_delete_batch = DeleteDomainBatch.Field()
    domain_update = UpdateDomain.Field()


class DomainQuery(graphene.ObjectType):
    domain = graphene.relay.Node.Field(DomainNode)
    domains = DjangoFilterConnectionField(
        DomainNode, orderBy=graphene.List(of_type=graphene.String)
    )

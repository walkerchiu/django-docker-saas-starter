from typing import Tuple
import uuid

from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError

from safedelete.models import HARD_DELETE

from tenant.models import Contract, Tenant
from tenant.services.domain_service import DomainService


class TenantService:
    @transaction.atomic
    def create_tenant(self, subdomain: str, email: str) -> Tuple[bool, Tenant]:
        schema_name = str(uuid.uuid4()).replace("-", "")

        tenant = Tenant(
            schema_name=schema_name,
            email=email,
        )
        tenant.save()

        try:
            # Add contract for the tenant
            contract = Contract(
                tenant=tenant,
                slug=schema_name,
            )
            contract.save()

            # Add a domain for the tenant
            domain_service = DomainService()
            domain_service.create_domain(
                tenant=tenant,
                value=subdomain + "." + settings.DOMAIN_WEBSITE,
                is_primary=True,
                is_builtin=True,
            )

        except IntegrityError:
            result = False
        else:
            result = True

        if not result:
            tenant.delete(force_policy=HARD_DELETE)
            tenant = None

        return result, tenant

    @transaction.atomic
    def updateEmail(self, email_original: str, email_new: str) -> bool:
        Tenant.all_objects.filter(email=email_original).update(email=email_new)

        return True

    @transaction.atomic
    def delete_tenant(self, tenant_id: uuid) -> bool:
        try:
            tenant = Tenant.objects.only("id").get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return False

        tenant.delete()

        return True

    @transaction.atomic
    def undelete_tenant(self, tenant_id: uuid) -> bool:
        try:
            tenant = Tenant.deleted_objects.only("id").get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return False

        tenant.undelete()

        return True

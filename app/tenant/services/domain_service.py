from typing import Tuple
import uuid

from django.db import transaction
from django.db.utils import IntegrityError

from safedelete.models import HARD_DELETE

from tenant.models import Domain, Tenant


class DomainService:
    @transaction.atomic
    def create_domain(
        self,
        tenant: Tenant,
        value: Domain,
        is_primary: bool = False,
        is_builtin: bool = False,
    ) -> Tuple[bool, Domain]:
        try:
            domain = Domain(
                tenant=tenant,
                domain=value,
                is_primary=is_primary,
                is_builtin=is_builtin,
            )
            domain.save()

            if is_primary:
                Domain.all_objects.filter(tenant=tenant, is_primary=True).exclude(
                    pk=domain.id
                ).update(is_primary=False)
        except IntegrityError:
            result = False
        else:
            result = True

        if not result:
            domain.delete(force_policy=HARD_DELETE)
            domain = None

        return result, domain

    @transaction.atomic
    def delete_domain(self, domain_id: uuid) -> bool:
        try:
            domain = Domain.objects.only("id").get(pk=domain_id, is_primary=False)
        except Domain.DoesNotExist:
            return False

        domain.delete()

        return True

    @transaction.atomic
    def update_domain(
        self,
        tenant: Tenant,
        id: uuid,
        value: Domain,
        is_primary: bool = False,
    ) -> Tuple[bool, Domain]:
        try:
            domain = Domain.objects.get(pk=id, tenant=tenant)

            domain.domain = value
            domain.is_primary = is_primary
            domain.save()

            if is_primary:
                Domain.all_objects.filter(tenant=tenant, is_primary=True).exclude(
                    pk=domain.id
                ).update(is_primary=False)
        except Domain.DoesNotExist:
            result = False
        except IntegrityError:
            result = False
        else:
            result = True

        if not result:
            domain = None

        return result, domain

    @transaction.atomic
    def undelete_domain(self, domain_id: uuid) -> bool:
        try:
            domain = Domain.deleted_objects.only("id").get(pk=domain_id)
        except Domain.DoesNotExist:
            return False

        domain.undelete()

        return True

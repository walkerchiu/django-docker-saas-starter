from typing import Tuple
import uuid

from django.db import transaction

from django_tenants.utils import schema_context
from safedelete.models import HARD_DELETE

from account.models import User
from account.services.user_service import UserService
from organization.models import Organization, OrganizationTrans
from role.services.role_service import RoleService


class OrganizationService:
    @transaction.atomic
    def initiate_schema(
        self, schema_name: str, organization_name: str, email: str, password: str
    ) -> Tuple[bool, Organization, User]:
        with schema_context(schema_name):
            organization = Organization(
                schema_name=schema_name,
            )
            organization.save()
            OrganizationTrans.objects.create(
                organization=organization,
                language_code=organization.language_code,
                name=organization_name,
            )

            result = self.init_default_data(organization)

            if result:
                user_service = UserService()
                result, user = user_service.create_user(
                    endpoint="dashboard",
                    email=email,
                    password=password,
                    username="demo",
                )
                if result:
                    role_service = RoleService()
                    user = role_service.assign_owner(
                        organization=organization,
                        user=user,
                    )

            if result:
                return result, organization, user
            else:
                organization.delete(force_policy=HARD_DELETE)
                return result, None, None

    @transaction.atomic
    def init_default_data(self, organization: Organization) -> bool:
        role_service = RoleService()
        result = role_service.init_default_data(organization)

        return result

    @transaction.atomic
    def delete_organization(self, schema_name: str, organization_id: uuid) -> bool:
        with schema_context(schema_name):
            try:
                organization = Organization.objects.only("id").get(pk=organization_id)
            except Organization.DoesNotExist:
                return False

            organization.delete()

        return True

    @transaction.atomic
    def undelete_organization(self, schema_name: str, organization_id: uuid) -> bool:
        with schema_context(schema_name):
            try:
                organization = Organization.deleted_objects.only("id").get(
                    pk=organization_id
                )
            except Organization.DoesNotExist:
                return False

            organization.undelete()

        return True

from typing import Type

from django.contrib.auth import get_user_model
from django.db import transaction

from organization.models import Organization
from role import ProtectedRole
from role.models import Role
from role.services.permission_service import PermissionService


class RoleService:
    @transaction.atomic
    def assign_admin(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_admin = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Admin
        )
        role_manager = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Manager
        )
        role_staff = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Staff
        )
        user.roles.add(role_admin)
        user.roles.add(role_manager)
        user.roles.add(role_staff)

        return user

    @transaction.atomic
    def assign_collaborator(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_collaborator = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Collaborator
        )
        user.roles.add(role_collaborator)

        return user

    @transaction.atomic
    def assign_customer(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_customer = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Customer
        )
        user.roles.add(role_customer)

        return user

    @transaction.atomic
    def assign_hq_user(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_hq_user = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.HQUser
        )
        user.roles.add(role_hq_user)

        return user

    @transaction.atomic
    def assign_manager(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_manager = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Manager
        )
        role_staff = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Staff
        )
        user.roles.add(role_manager)
        user.roles.add(role_staff)

        return user

    @transaction.atomic
    def assign_member(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_member = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Member
        )
        user.roles.add(role_member)

        return user

    @transaction.atomic
    def assign_owner(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_admin = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Admin
        )
        role_manager = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Manager
        )
        role_owner = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Owner
        )
        role_staff = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Staff
        )
        user.roles.add(role_admin)
        user.roles.add(role_manager)
        user.roles.add(role_owner)
        user.roles.add(role_staff)

        return user

    @transaction.atomic
    def assign_partner(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_partner = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Partner
        )
        user.roles.add(role_partner)

        return user

    @transaction.atomic
    def assign_staff(
        self, organization: Organization, user: Type[get_user_model()]
    ) -> Type[get_user_model()]:
        role_staff = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Staff
        )
        user.roles.add(role_staff)

        return user

    @transaction.atomic
    def init_default_data(self, organization: Organization) -> bool:
        role_admin, _ = Role.objects.get_or_create(
            organization=organization, slug=ProtectedRole.Admin
        )
        Role.objects.get_or_create(
            organization=organization, slug=ProtectedRole.Collaborator
        )
        Role.objects.get_or_create(
            organization=organization, slug=ProtectedRole.Customer
        )
        Role.objects.get_or_create(organization=organization, slug=ProtectedRole.HQUser)
        Role.objects.get_or_create(
            organization=organization, slug=ProtectedRole.Manager
        )
        Role.objects.get_or_create(organization=organization, slug=ProtectedRole.Member)
        Role.objects.get_or_create(organization=organization, slug=ProtectedRole.Owner)
        Role.objects.get_or_create(
            organization=organization, slug=ProtectedRole.Partner
        )
        Role.objects.get_or_create(organization=organization, slug=ProtectedRole.Staff)

        service_permission = PermissionService()
        (
            result,
            permission_assign_role,
            permission_assign_permission,
        ) = service_permission.init_default_data(organization)

        if result:
            role_admin.permissions.add(permission_assign_role)
            role_admin.permissions.add(permission_assign_permission)

        return result

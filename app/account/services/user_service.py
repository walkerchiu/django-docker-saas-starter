from typing import Tuple
import uuid

from account.models import Profile, User
from organization.models import Organization
from role import ProtectedRole
from role.models import Role


class UserService:
    def create_user(
        self, endpoint: str, email: str, password: str, username: str = ""
    ) -> Tuple[bool, User]:
        user = User(
            endpoint=endpoint,
            email=email,
            username=username,
        )
        user.set_password(password)
        user.save()

        Profile.objects.create(user=user)

        return True, user

    def delete_user(self, id: uuid) -> bool:
        try:
            user = User.objects.only("id").get(pk=id)
        except User.DoesNotExist:
            return False
        else:
            user.delete()

        return True

    def undelete_user(self, id: uuid) -> bool:
        try:
            user = User.deleted_objects.only("id").get(pk=id)
        except User.DoesNotExist:
            return False
        else:
            user.undelete()

        return True

    def assign_admin(self, organization: Organization, user: User) -> User:
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

    def assign_collaborator(self, organization: Organization, user: User) -> User:
        role_collaborator = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Collaborator
        )
        user.roles.add(role_collaborator)

        return user

    def assign_customer(self, organization: Organization, user: User) -> User:
        role_customer = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Customer
        )
        user.roles.add(role_customer)

        return user

    def assign_hq_user(self, organization: Organization, user: User) -> User:
        role_hq_user = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.HQUser
        )
        user.roles.add(role_hq_user)

        return user

    def assign_manager(self, organization: Organization, user: User) -> User:
        role_manager = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Manager
        )
        role_staff = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Staff
        )
        user.roles.add(role_manager)
        user.roles.add(role_staff)

        return user

    def assign_member(self, organization: Organization, user: User) -> User:
        role_member = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Member
        )
        user.roles.add(role_member)

        return user

    def assign_owner(self, organization: Organization, user: User) -> User:
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

    def assign_partner(self, organization: Organization, user: User) -> User:
        role_partner = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Partner
        )
        user.roles.add(role_partner)

        return user

    def assign_staff(self, organization: Organization, user: User) -> User:
        role_staff = Role.objects.only("id").get(
            organization=organization, slug=ProtectedRole.Staff
        )
        user.roles.add(role_staff)

        return user

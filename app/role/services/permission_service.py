from typing import Tuple

from django.db import transaction

from organization.models import Organization
from role import ProtectedPermission
from role.models import Permission


class PermissionService:
    @transaction.atomic
    def init_default_data(
        self, organization: Organization
    ) -> Tuple[bool, Permission, Permission]:
        permission_assign_role, _ = Permission.objects.get_or_create(
            organization=organization, slug=ProtectedPermission.AssignRole
        )

        permission_assign_permission, _ = Permission.objects.get_or_create(
            organization=organization, slug=ProtectedPermission.AssignPermission
        )

        return True, permission_assign_role, permission_assign_permission

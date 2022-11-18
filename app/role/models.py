import uuid

from django.conf import settings
from django.db import models

from safedelete.models import SOFT_DELETE_CASCADE

from core.models import CreateUpdateDateAndSafeDeleteMixin, TranslationModel
from organization.models import Organization


class Permission(CreateUpdateDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, models.CASCADE)
    slug = models.CharField(max_length=255, null=True, db_index=True)
    is_protected = models.BooleanField(default=False)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_role_permission"
        get_latest_by = "updated_at"
        index_together = (("organization", "slug"),)
        ordering = ["id"]

    def __str__(self):
        return str(self.id)


class PermissionTrans(CreateUpdateDateAndSafeDeleteMixin, TranslationModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    permission = models.ForeignKey(
        Permission, related_name="translations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_role_permission_trans"
        get_latest_by = "updated_at"
        index_together = (("language_code", "permission"),)
        ordering = ["language_code"]

    def __str__(self):
        return str(self.id)


class Role(CreateUpdateDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, models.CASCADE)
    permissions = models.ManyToManyField(Permission)
    slug = models.CharField(max_length=255, null=True, db_index=True)
    is_protected = models.BooleanField(default=False)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_role_role"
        get_latest_by = "updated_at"
        index_together = (("organization", "slug"),)
        ordering = ["id"]

    def __str__(self):
        return str(self.id)


class RoleTrans(CreateUpdateDateAndSafeDeleteMixin, TranslationModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role, related_name="translations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_role_role_trans"
        get_latest_by = "updated_at"
        index_together = (("language_code", "role"),)
        ordering = ["language_code"]

    def __str__(self):
        return str(self.id)

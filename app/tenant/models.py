import uuid

from django.conf import settings
from django.db import models

from django_tenants.models import TenantMixin, DomainMixin
from safedelete.models import SOFT_DELETE_CASCADE

from core.models import CommonDateAndSafeDeleteMixin, PublishableModel


class Tenant(TenantMixin, CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schema_name = models.CharField(max_length=32)
    email = models.EmailField(
        verbose_name="email address", max_length=255, db_index=True
    )

    _safedelete_policy = SOFT_DELETE_CASCADE
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        db_table = settings.APP_NAME + "_tenant_tenant"
        ordering = ["id"]

    def __str__(self):
        return str(self.id)


class Contract(CommonDateAndSafeDeleteMixin, PublishableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, models.CASCADE)
    slug = models.CharField(max_length=32, unique=True, db_index=True)
    type = models.CharField(max_length=10, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    effective_from = models.DateTimeField(null=True)
    expired_on = models.DateTimeField(null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_tenant_contract"
        ordering = ["slug"]

    def __str__(self):
        return self.slug


class Domain(DomainMixin, CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        settings.TENANT_MODEL,
        db_index=True,
        related_name="domains",
        on_delete=models.CASCADE,
    )
    domain = models.CharField(max_length=253, db_index=True)
    is_builtin = models.BooleanField(default=False)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_tenant_domain"
        ordering = ["domain"]

    def __str__(self):
        return str(self.id)


class Job(CommonDateAndSafeDeleteMixin, PublishableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    schema_name = models.CharField(max_length=32, blank=True, null=True)
    month = models.CharField(max_length=2, blank=True, null=True)
    weekday = models.CharField(max_length=1, blank=True, null=True)
    time = models.CharField(max_length=5, blank=True, null=True)
    sort_key = models.IntegerField(db_index=True, null=True)

    class Meta:
        db_table = settings.APP_NAME + "_job"
        get_latest_by = "updated_at"
        ordering = ["sort_key"]

    def __str__(self):
        return str(self.id)


class Task(CommonDateAndSafeDeleteMixin, PublishableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Job,
        db_index=True,
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    sort_key = models.IntegerField(db_index=True, null=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        db_table = settings.APP_NAME + "_task"
        get_latest_by = "updated_at"
        ordering = ["sort_key"]

    def __str__(self):
        return str(self.id)

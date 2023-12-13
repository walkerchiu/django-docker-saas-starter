import uuid

from django.db import models

from account.models import User
from core.models import CommonDateAndSafeDeleteMixin


class Log(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, models.CASCADE)
    action = models.CharField(max_length=255, db_index=True)
    ip = models.GenericIPAddressField(db_index=True, null=True)
    location = models.CharField(max_length=255, db_index=True, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class LogDetail(CommonDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log = models.OneToOneField(Log, models.CASCADE)
    header = models.TextField(blank=True, null=True)
    request = models.TextField(blank=True, null=True)
    variables = models.JSONField(blank=True, null=True)
    response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

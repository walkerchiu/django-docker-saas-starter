from django.db import connection
from django.utils.timezone import datetime

from tenant.models import Contract


class ContractHelper:
    def __init__(self, schema_name: str = connection.schema_name):
        self.schema_name = schema_name

    def check_if_it_has_expired(
        self,
    ) -> bool:
        return (
            Contract.objects.filter(tenant__schema_name=self.schema_name)
            .filter(expired_on__gt=datetime.now())
            .exists()
        )

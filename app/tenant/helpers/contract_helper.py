from django.db import connection
from django.utils.timezone import datetime

from tenant.models import Contract


class ContractHelper:
    def __init__(self, schema_name: str = connection.schema_name):
        self.schema_name = schema_name

    def check_if_it_is_within_the_validity_period(
        self,
    ) -> bool:
        return (
            Contract.objects.filter(tenant__schema_name=self.schema_name)
            .filter(effective_from__lt=datetime.now(), expired_on__gt=datetime.now())
            .exists()
        )

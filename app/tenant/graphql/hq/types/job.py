from graphene import ResolveInfo
from graphene_django import DjangoObjectType
import graphene

from core.relay.connection import ExtendedConnection
from tenant.models import Job


class JobType(DjangoObjectType):
    class Meta:
        model = Job
        fields = (
            "id",
            "name",
            "description",
            "month",
            "weekday",
            "time",
            "sort_key",
        )


class JobConnection(graphene.relay.Connection):
    class Meta:
        node = JobType


class JobNode(DjangoObjectType):
    class Meta:
        model = Job
        filter_fields = {
            "id": ["exact"],
            "name": ["exact"],
        }
        order_by_field = "sort_key"
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            tenant = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return tenant

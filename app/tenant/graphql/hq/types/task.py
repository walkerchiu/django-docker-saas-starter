from graphene import ResolveInfo
from graphene_django import DjangoObjectType
import graphene

from core.relay.connection import ExtendedConnection
from tenant.models import Task


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = (
            "id",
            "sort_key",
            "is_locked",
        )


class TaskConnection(graphene.relay.Connection):
    class Meta:
        node = TaskType


class TaskNode(DjangoObjectType):
    class Meta:
        model = Task
        filter_fields = {
            "id": ["exact"],
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

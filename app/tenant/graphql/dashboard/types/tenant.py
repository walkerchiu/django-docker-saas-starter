from django_filters import (
    CharFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
import graphene

from core.relay.connection import ExtendedConnection
from tenant.models import Tenant


class TenantType(DjangoObjectType):
    class Meta:
        model = Tenant
        fields = (
            "id",
            "email",
        )


class TenantFilter(FilterSet):
    email = CharFilter(field_name="email", lookup_expr="exact")
    created_at_gt = DateTimeFilter(field_name="created_at", lookup_expr="gt")
    created_at_gte = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_lt = DateTimeFilter(field_name="created_at", lookup_expr="lt")
    created_at_lte = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_at_gt = DateTimeFilter(field_name="updated_at", lookup_expr="gt")
    updated_at_gte = DateTimeFilter(field_name="updated_at", lookup_expr="gte")
    updated_at_lt = DateTimeFilter(field_name="updated_at", lookup_expr="lt")
    updated_at_lte = DateTimeFilter(field_name="updated_at", lookup_expr="lte")

    class Meta:
        model = Tenant
        fields = []

    order_by = OrderingFilter(
        fields=(
            "email",
            "created_at",
            "updated_at",
        )
    )


class TenantConnection(graphene.relay.Connection):
    class Meta:
        node = TenantType


class TenantNode(DjangoObjectType):
    class Meta:
        model = Tenant
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = TenantFilter
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

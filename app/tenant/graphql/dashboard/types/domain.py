from django_filters import (
    BooleanFilter,
    CharFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
import graphene

from core.relay.connection import ExtendedConnection
from tenant.models import Domain


class DomainType(DjangoObjectType):
    class Meta:
        model = Domain
        fields = (
            "id",
            "domain",
            "is_builtin",
            "is_primary",
        )


class DomainFilter(FilterSet):
    domain = CharFilter(field_name="domain", lookup_expr="exact")
    is_builtin = BooleanFilter(field_name="is_builtin")
    is_primary = BooleanFilter(field_name="is_primary")
    created_at_gt = DateTimeFilter(field_name="created_at", lookup_expr="gt")
    created_at_gte = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_lt = DateTimeFilter(field_name="created_at", lookup_expr="lt")
    created_at_lte = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_at_gt = DateTimeFilter(field_name="updated_at", lookup_expr="gt")
    updated_at_gte = DateTimeFilter(field_name="updated_at", lookup_expr="gte")
    updated_at_lt = DateTimeFilter(field_name="updated_at", lookup_expr="lt")
    updated_at_lte = DateTimeFilter(field_name="updated_at", lookup_expr="lte")

    class Meta:
        model = Domain
        fields = []

    order_by = OrderingFilter(
        fields=(
            "domain",
            "created_at",
            "updated_at",
        )
    )


class DomainConnection(graphene.relay.Connection):
    class Meta:
        node = DomainType


class DomainNode(DjangoObjectType):
    class Meta:
        model = Domain
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = DomainFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            domain = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return domain

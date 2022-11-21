from django_filters import (
    CharFilter,
    DateFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
import graphene

from core.relay.connection import ExtendedConnection
from tenant.models import Contract


class ContractType(DjangoObjectType):
    class Meta:
        model = Contract
        fields = (
            "id",
            "slug",
            "type",
            "note",
            "expired_on",
        )


class ContractFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")
    type = CharFilter(field_name="type", lookup_expr="exact")
    note = CharFilter(field_name="note", lookup_expr="icontains")
    expired_on_gt = DateFilter(field_name="expired_on", lookup_expr="gt")
    expired_on_gte = DateFilter(field_name="expired_on", lookup_expr="gte")
    expired_on_lt = DateFilter(field_name="expired_on", lookup_expr="lt")
    created_at_gt = DateTimeFilter(field_name="created_at", lookup_expr="gt")
    created_at_gte = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_lt = DateTimeFilter(field_name="created_at", lookup_expr="lt")
    created_at_lte = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_at_gt = DateTimeFilter(field_name="updated_at", lookup_expr="gt")
    updated_at_gte = DateTimeFilter(field_name="updated_at", lookup_expr="gte")
    updated_at_lt = DateTimeFilter(field_name="updated_at", lookup_expr="lt")
    updated_at_lte = DateTimeFilter(field_name="updated_at", lookup_expr="lte")

    class Meta:
        model = Contract
        fields = []

    order_by = OrderingFilter(
        fields=(
            "slug",
            "type",
            "expired_on",
            "created_at",
            "updated_at",
        )
    )


class ContractConnection(graphene.relay.Connection):
    class Meta:
        node = ContractType


class ContractNode(DjangoObjectType):
    class Meta:
        model = Contract
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = ContractFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            contract = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return contract

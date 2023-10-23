from django.core.exceptions import ValidationError

from django_filters import (
    CharFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
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
            "effective_from",
            "expired_on",
        )


class ContractFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")
    type = CharFilter(field_name="type", lookup_expr="exact")
    note = CharFilter(field_name="note", lookup_expr="icontains")
    effective_from_gt = DateTimeFilter(field_name="effective_from", lookup_expr="gt")
    effective_from_gte = DateTimeFilter(field_name="effective_from", lookup_expr="gte")
    effective_from_lt = DateTimeFilter(field_name="effective_from", lookup_expr="lt")
    expired_on_gt = DateTimeFilter(field_name="expired_on", lookup_expr="gt")
    expired_on_gte = DateTimeFilter(field_name="expired_on", lookup_expr="gte")
    expired_on_lt = DateTimeFilter(field_name="expired_on", lookup_expr="lt")
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
            "effective_from",
            "expired_on",
            "created_at",
            "updated_at",
        )
    )


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
            raise ValidationError("Bad Request!")

        return contract


class ContractConnection(graphene.relay.Connection):
    class Meta:
        node = ContractType

from django_filters import (
    CharFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene import ResolveInfo
from graphene_django import DjangoConnectionField, DjangoObjectType
import graphene

from core.relay.connection import ExtendedConnection
from tenant.graphql.dashboard.types.contract import ContractNode
from tenant.graphql.dashboard.types.domain import DomainNode
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

    contract_set = DjangoConnectionField(
        ContractNode, orderBy=graphene.List(of_type=graphene.String)
    )
    domain_set = DjangoConnectionField(
        DomainNode, orderBy=graphene.List(of_type=graphene.String)
    )

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        raise Exception("This operation is not allowed!")

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            tenant = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return tenant

    @staticmethod
    def resolve_contractSet(root: Tenant, info: ResolveInfo, **kwargs):
        return info.context.loaders.contracts_by_tenant_loader.load(root.id)

    @staticmethod
    def resolve_domainSet(root: Tenant, info: ResolveInfo, **kwargs):
        return info.context.loaders.domains_by_tenant_loader.load(root.id)


class TenantConnection(graphene.relay.Connection):
    class Meta:
        node = TenantType

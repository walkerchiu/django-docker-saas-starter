from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphene import ResolveInfo
import graphene

from core.relay.connection import ExtendedConnection
from tenant.models import Tenant


class TenantType(DjangoObjectType):
    class Meta:
        model = Tenant
        fields = ("id",)


class RegisterTenantResponseType(graphene.ObjectType):
    domain = graphene.String()
    token = graphene.String()
    payload = graphene.types.generic.GenericScalar()


class TenantConnection(graphene.relay.Connection):
    class Meta:
        node = TenantType


class TenantNode(DjangoObjectType):
    class Meta:
        model = Tenant
        filter_fields = {
            "id": ["exact"],
        }
        fields = ("id",)
        order_by_field = "id"
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info: ResolveInfo):
        raise Exception("This operation is not allowed!")

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            tenant = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        if (
            info.context.user.is_authenticated
            and info.context.user.is_staff
            and info.context.tenant == tenant
        ):
            return tenant

        raise Exception("Bad Request!")

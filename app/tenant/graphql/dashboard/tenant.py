from graphene_django.filter import DjangoFilterConnectionField
import graphene

from tenant.graphql.dashboard.types.tenant import TenantNode


class TenantQuery(graphene.ObjectType):
    tenant = graphene.relay.Node.Field(TenantNode)
    tenants = DjangoFilterConnectionField(
        TenantNode, orderBy=graphene.List(of_type=graphene.String)
    )


class TenantMutation(graphene.ObjectType):
    pass
